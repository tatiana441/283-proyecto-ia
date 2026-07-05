"""Limpieza de las dos fuentes de precios.

1. SISMED compactado: parquet generado por el equipo con Spark a partir de ~23M
   de registros (2017-01 a 2019-06). Se corrige encoding, se tratan los ceros
   como "no reportado" y se agrega a Mes × ExpedienteCum × TipoReporte para
   que quepa en Supabase (free tier). Es histórico de referencia, NO precio actual.

2. Precios Máximos de Venta regulados (CNPMDM, Circular 19/2024, `nauz-qkjw`):
   precio techo vigente por CUM. Se separa la llave `cum` en expediente y
   consecutivo para cruzar con el catálogo CUM.
"""

from pathlib import Path

import pandas as pd

from src.common import DATA_EXTERNAL, DATA_PROCESSED, REPO_ROOT, load_config

PRECIO_COLS = ["PromedioValorMinimo", "PromedioValorMaximo", "ValorPromedio", "PromedioValorTotal"]


def _arreglar_mojibake(serie: pd.Series) -> pd.Series:
    """Repara texto UTF-8 leído como Latin-1 en el pipeline de origen (p. ej. 'INSTITUCIÃ“N')."""
    def fix(v):
        if not isinstance(v, str):
            return v
        try:
            reparado = v.encode("latin1").decode("utf-8")
            return reparado if "Ã" in v or "Â" in v else v
        except (UnicodeEncodeError, UnicodeDecodeError):
            return v
    return serie.map(fix)


def limpiar_sismed(parquet_dir=None) -> pd.DataFrame | None:
    """Lee el parquet compactado, limpia y agrega a Mes × ExpedienteCum × TipoReporte.

    Si el parquet no está disponible (p. ej. en CI/cron: es un archivo local de
    230 MB que no viaja al repo), devuelve None y la tabla existente en Supabase
    se conserva — el histórico SISMED es estático (2017-2019).
    """
    if parquet_dir is None:
        parquet_dir = REPO_ROOT / load_config()["sismed"]["parquet_dir"]

    parquet_dir = Path(parquet_dir)
    if not parquet_dir.exists() or not any(parquet_dir.glob("*.parquet")):
        print(f"[clean_precios] SISMED: parquet no disponible en {parquet_dir}; se omite (tabla existente se conserva)")
        return None

    df = pd.read_parquet(parquet_dir)
    print(f"[clean_precios] SISMED crudo: {len(df):,} filas")

    for col in ["TipoEntidadDesc", "DescripcionComercial", "Descripcion_Atc", "FormaFarmaceutica"]:
        if col in df.columns:
            df[col] = _arreglar_mojibake(df[col])

    # Precios en 0 = no reportado -> NA (no son precios reales)
    for col in PRECIO_COLS:
        df[col] = df[col].mask(df[col] <= 0)

    # Winsorizar outliers absurdos (hay maximos de ~10^11 COP) al percentil 99.5
    for col in PRECIO_COLS:
        tope = df[col].quantile(0.995)
        df[col] = df[col].clip(upper=tope)

    df["PromedioUnidadeso"] = df["PromedioUnidadeso"].mask(df["PromedioUnidadeso"] <= 0)

    agg = (
        df.groupby(["Mes", "ExpedienteCum", "TipoReportePrecioDesc"], as_index=False)
        .agg(
            precio_promedio=("ValorPromedio", "mean"),
            precio_minimo=("PromedioValorMinimo", "min"),
            precio_maximo=("PromedioValorMaximo", "max"),
            unidades=("PromedioUnidadeso", "sum"),
            valor_total=("PromedioValorTotal", "sum"),
            n_registros=("ValorPromedio", "size"),
        )
        .rename(columns={"Mes": "mes", "ExpedienteCum": "expediente", "TipoReportePrecioDesc": "tipo_reporte"})
    )
    # Sin ningun precio reportado en el grupo -> fila sin informacion util
    agg = agg.dropna(subset=["precio_promedio", "precio_minimo", "precio_maximo"], how="all")

    out = DATA_PROCESSED / "precios"
    out.mkdir(parents=True, exist_ok=True)
    agg.to_csv(out / "precios_mensuales.csv", index=False, encoding="utf-8")
    print(f"[clean_precios] precios_mensuales (agregado): {len(agg):,} filas")
    return agg


def limpiar_precios_regulados(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia la base de precios máximos regulados (nauz-qkjw)."""
    df = df_raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    renombres = {
        "precio_maximo_de_venta_transaccion_primaria_secundaria_y_final_institucional": "pmax_institucional",
        "precio_maximo_de_venta_transaccion_primaria_y_secundaria_comercial": "pmax_comercial_mayorista",
        "precio_maximo_de_venta_transaccion_final_comercial": "pmax_comercial_final",
        "fecha_de_inicio_vigencia_precio_maximo_de_venta": "fecha_inicio_vigencia",
        "circular_cnpmdm": "circular",
        "cantidad_por_unidad_de_medida": "cantidad_unidad_medida",
    }
    df = df.rename(columns=renombres)

    df["cum"] = df["cum"].astype("string").str.strip().str.upper()
    partes = df["cum"].str.split("-", n=1)
    df["expediente"] = pd.to_numeric(partes.str[0], errors="coerce").astype("Int64")
    df["consecutivo"] = pd.to_numeric(partes.str[1], errors="coerce").astype("Int64")

    for col in ["pmax_institucional", "pmax_comercial_mayorista", "pmax_comercial_final", "margen_para_ips", "cantidad_unidad_medida"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["fecha_inicio_vigencia"] = pd.to_datetime(df["fecha_inicio_vigencia"], errors="coerce")

    cols = [
        "cum", "expediente", "consecutivo", "id_mr", "mercado_relevante", "medicamento",
        "cantidad_unidad_medida", "unidad_de_medida", "pmax_institucional",
        "pmax_comercial_mayorista", "pmax_comercial_final", "margen_para_ips",
        "circular", "fecha_inicio_vigencia",
    ]
    df = df[[c for c in cols if c in df.columns]].drop_duplicates(subset=["cum"])

    out = DATA_PROCESSED / "precios"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "precios_regulados.csv", index=False, encoding="utf-8")
    print(f"[clean_precios] precios_regulados: {len(df):,} filas")
    return df
