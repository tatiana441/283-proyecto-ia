"""Panel de features mensuales por principio activo para el score de riesgo.

Cada fila es (principio_activo, mes) sobre una malla completa de meses, de modo
que los meses sin solicitudes cuentan como 0 (necesario para recencia y modelo).
Todas las features usan solo información pasada (t o anterior) — sin fuga temporal.
"""

import pandas as pd

from src.common import DATA_PROCESSED
from src.data_pipeline.integrate import normalize_text


def construir_panel(solicitudes: pd.DataFrame) -> pd.DataFrame:
    """Construye el panel PA × mes con features de riesgo."""
    df = solicitudes.copy()
    df["pa"] = df["principio_activo_1"].map(normalize_text)
    df = df.dropna(subset=["pa", "mes_autorizacion"])
    df["es_urgencia"] = (
        df["tipo_solicitud"].astype("string").str.upper().str.contains("URGENCIA", na=False)
    )

    base = (
        df.groupby(["pa", "mes_autorizacion"])
        .agg(
            n_solicitudes=("pa", "size"),
            cantidad_total=("cantidad_solicitada_num", "sum"),
            n_solicitantes=("solicitante_importador", "nunique"),
            n_urgencia=("es_urgencia", "sum"),
        )
        .reset_index()
        .rename(columns={"mes_autorizacion": "mes"})
    )

    # Malla completa de meses por PA (los ceros importan)
    meses = pd.period_range(base["mes"].min(), base["mes"].max(), freq="M").astype(str)
    pas = base["pa"].unique()
    malla = pd.MultiIndex.from_product([pas, meses], names=["pa", "mes"]).to_frame(index=False)
    panel = malla.merge(base, on=["pa", "mes"], how="left").fillna(
        {"n_solicitudes": 0, "cantidad_total": 0, "n_solicitantes": 0, "n_urgencia": 0}
    )
    panel = panel.sort_values(["pa", "mes"]).reset_index(drop=True)

    g = panel.groupby("pa", sort=False)
    panel["sol_3m"] = g["n_solicitudes"].transform(lambda s: s.rolling(3, min_periods=1).sum())
    panel["sol_6m"] = g["n_solicitudes"].transform(lambda s: s.rolling(6, min_periods=1).sum())
    panel["sol_12m"] = g["n_solicitudes"].transform(lambda s: s.rolling(12, min_periods=1).sum())
    panel["solicitantes_12m"] = g["n_solicitantes"].transform(lambda s: s.rolling(12, min_periods=1).sum())
    panel["urgencia_6m"] = g["n_urgencia"].transform(lambda s: s.rolling(6, min_periods=1).sum())
    panel["pct_urgencia_6m"] = (panel["urgencia_6m"] / panel["sol_6m"].replace(0, pd.NA)).fillna(0.0)

    # Tendencia: trimestre actual vs trimestre anterior
    panel["sol_3m_prev"] = g["sol_3m"].transform(lambda s: s.shift(3)).fillna(0)
    panel["tendencia_3m"] = panel["sol_3m"] - panel["sol_3m_prev"]

    # Recencia: meses desde la última solicitud (99 = nunca ha tenido)
    def _recencia(s: pd.Series) -> pd.Series:
        idx = pd.Series(range(len(s)), index=s.index)
        ultimo = idx.where(s.to_numpy() > 0).ffill()
        return (idx - ultimo).fillna(99)

    panel["recencia_meses"] = g["n_solicitudes"].transform(_recencia)

    return panel


FEATURES_MODELO = [
    "n_solicitudes", "sol_3m", "sol_6m", "sol_12m",
    "solicitantes_12m", "pct_urgencia_6m", "tendencia_3m", "recencia_meses",
]


def agregar_label(panel: pd.DataFrame, horizonte: int = 3) -> pd.DataFrame:
    """y = 1 si el PA registra solicitudes en los `horizonte` meses siguientes.

    Las filas de los últimos `horizonte` meses quedan sin label (NaN) y se
    excluyen del entrenamiento.
    """
    panel = panel.sort_values(["pa", "mes"]).copy()
    g = panel.groupby("pa", sort=False)["n_solicitudes"]
    futuro = sum(g.shift(-i) for i in range(1, horizonte + 1))
    panel["y"] = (futuro > 0).astype("Int64").where(futuro.notna())
    return panel


def run(solicitudes: pd.DataFrame | None = None) -> pd.DataFrame:
    if solicitudes is None:
        solicitudes = pd.read_csv(DATA_PROCESSED / "vitales" / "solicitudes.csv")
    panel = construir_panel(solicitudes)
    out = DATA_PROCESSED / "features"
    out.mkdir(parents=True, exist_ok=True)
    panel.to_csv(out / "panel_riesgo.csv", index=False, encoding="utf-8")
    print(f"[features] panel: {len(panel):,} filas ({panel['pa'].nunique()} PAs × {panel['mes'].nunique()} meses)")
    return panel
