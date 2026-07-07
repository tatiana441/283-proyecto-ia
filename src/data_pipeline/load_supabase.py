"""Carga de las tablas procesadas a Supabase (Postgres).

- DDL por tabla: solo se recrean las tablas que traen datos en esta corrida
  (una corrida sin el parquet SISMED no borra precios_mensuales existentes).
- risk_scores y chat_logs NUNCA se tumban aquí: risk_scores lo refresca
  src/inference.py y chat_logs es historial de usuarios.
- Carga masiva con COPY vía psycopg (157k+ filas; supabase-py sería lento).
- RLS: lectura pública (anon) en catálogos; chat_logs solo autenticado.
"""

import io

import pandas as pd
import psycopg

from src.common import database_url

TABLAS_DDL = {
    "productos": """CREATE TABLE productos (
        expediente BIGINT, producto TEXT, titular TEXT, registrosanitario TEXT,
        fechaexpedicion DATE, fechavencimiento DATE, estadoregistro TEXT)""",
    "presentaciones": """CREATE TABLE presentaciones (
        cum TEXT, cum_std TEXT, expedientecum BIGINT, consecutivocum INT,
        cantidadcum DOUBLE PRECISION, unidad TEXT, descripcioncomercial TEXT,
        estadocum TEXT, fechaactivo DATE, fechainactivo DATE,
        muestramedica TEXT, formafarmaceutica TEXT)""",
    "principios_activos_cum": """CREATE TABLE principios_activos_cum (
        cum TEXT, expediente BIGINT, principioactivo TEXT, concentracion TEXT,
        cantidad DOUBLE PRECISION, unidadreferencia TEXT, atc TEXT,
        descripcionatc TEXT, atc_valido BOOLEAN)""",
    "medicamentos_vitales": """CREATE TABLE medicamentos_vitales (
        ium TEXT, nombre_comercial TEXT, forma_farmaceutica TEXT,
        presentacion_comercial TEXT, principio_activo_1 TEXT,
        concentracion_medicamento_1 TEXT, unidad_medida_1 TEXT,
        principio_activo_2 TEXT, concentracion_medicamento_2 TEXT, unidad_medida_2 TEXT)""",
    "solicitudes": """CREATE TABLE solicitudes (
        fecha_autorizacion DATE, anio_autorizacion INT, mes_autorizacion TEXT,
        tipo_solicitud TEXT, solicitante_importador TEXT, ium TEXT,
        principio_activo_1 TEXT, cantidad_solicitada DOUBLE PRECISION)""",
    "diagnosticos": """CREATE TABLE diagnosticos (
        ium TEXT, diagnostico_cie_descripcion TEXT, codigo_diagnostico_cie10 TEXT,
        sin_diagnostico BOOLEAN, codigo_cie10_valido BOOLEAN)""",
    "match_principio_activo": """CREATE TABLE match_principio_activo (
        nombre_vitales TEXT, nombre_cum TEXT, metodo TEXT, score DOUBLE PRECISION)""",
    "precios_mensuales": """CREATE TABLE precios_mensuales (
        mes TEXT, expediente BIGINT, tipo_reporte TEXT,
        precio_promedio DOUBLE PRECISION, precio_minimo DOUBLE PRECISION,
        precio_maximo DOUBLE PRECISION, unidades DOUBLE PRECISION,
        valor_total DOUBLE PRECISION, n_registros INT)""",
    "precios_regulados": """CREATE TABLE precios_regulados (
        cum TEXT, expediente BIGINT, consecutivo INT, id_mr TEXT,
        mercado_relevante TEXT, medicamento TEXT,
        cantidad_unidad_medida DOUBLE PRECISION, unidad_de_medida TEXT,
        pmax_institucional DOUBLE PRECISION, pmax_comercial_mayorista DOUBLE PRECISION,
        pmax_comercial_final DOUBLE PRECISION, margen_para_ips DOUBLE PRECISION,
        circular TEXT, fecha_inicio_vigencia DATE)""",
}

INDICES = {
    "productos": ["CREATE INDEX ON productos (expediente)"],
    "presentaciones": ["CREATE INDEX ON presentaciones (expedientecum)"],
    "principios_activos_cum": [
        "CREATE INDEX ON principios_activos_cum (expediente)",
        "CREATE INDEX ON principios_activos_cum (principioactivo)",
    ],
    "solicitudes": [
        "CREATE INDEX ON solicitudes (ium)",
        "CREATE INDEX ON solicitudes (mes_autorizacion)",
        "CREATE INDEX ON solicitudes (principio_activo_1)",
    ],
    "precios_mensuales": ["CREATE INDEX ON precios_mensuales (expediente, mes)"],
    "precios_regulados": ["CREATE INDEX ON precios_regulados (expediente)"],
    "match_principio_activo": ["CREATE INDEX ON match_principio_activo (nombre_vitales)"],
}

# Tablas que el pipeline no debe tumbar jamás (las llenan otros procesos)
DDL_PERMANENTES = """
CREATE TABLE IF NOT EXISTS risk_scores (
    principio_activo TEXT, mes TEXT, score DOUBLE PRECISION, nivel TEXT,
    tendencia TEXT, factores JSONB, prob_ml DOUBLE PRECISION,
    calculado_en TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS chat_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, user_id UUID,
    pregunta TEXT, respuesta TEXT, sources JSONB, creado_en TIMESTAMPTZ DEFAULT now());
"""

CATALOGOS_PUBLICOS = list(TABLAS_DDL.keys()) + ["risk_scores"]

MAPEOS = {
    "productos": {
        "expediente": "expediente", "producto": "producto", "titular": "titular",
        "registrosanitario": "registrosanitario", "fechaexpedicion": "fechaexpedicion_limpia",
        "fechavencimiento": "fechavencimiento_limpia", "estadoregistro": "estadoregistro",
    },
    "presentaciones": {
        "cum": "cum", "cum_std": "cum_std", "expedientecum": "expedientecum",
        "consecutivocum": "consecutivocum", "cantidadcum": "cantidadcum_num",
        "unidad": "unidad", "descripcioncomercial": "descripcioncomercial",
        "estadocum": "estadocum", "fechaactivo": "fechaactivo_limpia",
        "fechainactivo": "fechainactivo_limpia", "muestramedica": "muestramedica",
        "formafarmaceutica": "formafarmaceutica",
    },
    "principios_activos_cum": {
        "cum": "cum", "expediente": "expediente", "principioactivo": "principioactivo",
        "concentracion": "concentracion", "cantidad": "cantidad_num",
        "unidadreferencia": "unidadreferencia", "atc": "atc",
        "descripcionatc": "descripcionatc", "atc_valido": "atc_valido",
    },
    "medicamentos_vitales": {c: c for c in [
        "ium", "nombre_comercial", "forma_farmaceutica", "presentacion_comercial",
        "principio_activo_1", "concentracion_medicamento_1", "unidad_medida_1",
        "principio_activo_2", "concentracion_medicamento_2", "unidad_medida_2"]},
    "solicitudes": {
        "fecha_autorizacion": "fecha_autorizacion_limpia", "anio_autorizacion": "anio_autorizacion",
        "mes_autorizacion": "mes_autorizacion", "tipo_solicitud": "tipo_solicitud",
        "solicitante_importador": "solicitante_importador", "ium": "ium",
        "principio_activo_1": "principio_activo_1", "cantidad_solicitada": "cantidad_solicitada_num",
    },
    "diagnosticos": {c: c for c in [
        "ium", "diagnostico_cie_descripcion", "codigo_diagnostico_cie10",
        "sin_diagnostico", "codigo_cie10_valido"]},
    "match_principio_activo": {c: c for c in ["nombre_vitales", "nombre_cum", "metodo", "score"]},
    "precios_mensuales": {c: c for c in [
        "mes", "expediente", "tipo_reporte", "precio_promedio", "precio_minimo",
        "precio_maximo", "unidades", "valor_total", "n_registros"]},
    "precios_regulados": {c: c for c in [
        "cum", "expediente", "consecutivo", "id_mr", "mercado_relevante", "medicamento",
        "cantidad_unidad_medida", "unidad_de_medida", "pmax_institucional",
        "pmax_comercial_mayorista", "pmax_comercial_final", "margen_para_ips",
        "circular", "fecha_inicio_vigencia"]},
}


def _copy_dataframe(cur, tabla: str, df: pd.DataFrame, columnas: dict[str, str]) -> int:
    presentes = {dest: orig for dest, orig in columnas.items() if orig in df.columns}
    sub = df[list(presentes.values())].copy()
    sub.columns = list(presentes.keys())

    buf = io.StringIO()
    sub.to_csv(buf, index=False, header=False, na_rep="")
    buf.seek(0)

    cols_sql = ", ".join(presentes.keys())
    with cur.copy(f"COPY {tabla} ({cols_sql}) FROM STDIN WITH (FORMAT csv, NULL '')") as copy:
        copy.write(buf.getvalue())
    return len(sub)


def aplicar_rls(cur) -> None:
    for tabla in CATALOGOS_PUBLICOS:
        cur.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY;")
        cur.execute(f'DROP POLICY IF EXISTS "lectura_publica_{tabla}" ON {tabla};')
        cur.execute(
            f'CREATE POLICY "lectura_publica_{tabla}" ON {tabla} '
            f"FOR SELECT TO anon, authenticated USING (true);"
        )
        cur.execute(f"GRANT SELECT ON {tabla} TO anon, authenticated;")

    cur.execute("ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;")
    cur.execute('DROP POLICY IF EXISTS "chat_propio" ON chat_logs;')
    cur.execute(
        'CREATE POLICY "chat_propio" ON chat_logs FOR ALL TO authenticated '
        "USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());"
    )
    cur.execute("GRANT SELECT, INSERT ON chat_logs TO authenticated;")


def run(tablas: dict[str, pd.DataFrame | None]) -> None:
    """Recrea y carga solo las tablas con datos en esta corrida."""
    url = database_url()
    with psycopg.connect(url, connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL_PERMANENTES)
            for tabla, ddl in TABLAS_DDL.items():
                df = tablas.get(tabla)
                if df is None or df.empty:
                    print(f"[load] {tabla}: sin datos en esta corrida, se conserva la tabla existente")
                    continue
                cur.execute(f"DROP TABLE IF EXISTS {tabla} CASCADE")
                cur.execute(ddl)
                for idx in INDICES.get(tabla, []):
                    cur.execute(idx)
                n = _copy_dataframe(cur, tabla, df, MAPEOS[tabla])
                print(f"[load] {tabla}: {n:,} filas cargadas")
            aplicar_rls(cur)
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            print(f"[load] tamaño BD tras la carga: {cur.fetchone()[0]}")
