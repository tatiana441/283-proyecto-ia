"""Herramientas de datos que el agente conversacional puede invocar.

Cada herramienta consulta Supabase (mismas consultas que la API REST) y devuelve
(resultado, source): el resultado va al LLM como contexto y el source alimenta
la trazabilidad `sources[]` que se muestra en la interfaz.
"""

import json

from src.api.db import query

_NORM = "unaccent(upper({}))"

FUENTES = {
    "cum": "INVIMA — Código Único de Medicamentos Vigentes (datos.gov.co i7cb-raxc)",
    "vitales": "INVIMA — Medicamentos Vitales No Disponibles (datos.gov.co sdmr-tfmf)",
    "sismed": "MinSalud — SISMED histórico 2017-2019 (compactado)",
    "regulados": "CNPMDM — Precios Máximos de Venta, Circular 19/2024 (datos.gov.co nauz-qkjw)",
    "score": "MediWatch — score de riesgo calculado sobre Vitales No Disponibles",
}


def buscar_medicamento(nombre: str, limite: int = 5):
    patron = f"%{nombre.strip()}%"
    filas = query(
        f"""
        SELECT p.expediente, max(p.producto) AS producto, max(p.titular) AS titular,
               max(p.estadoregistro) AS estado,
               array_agg(DISTINCT pa.principioactivo) AS principios_activos,
               max(rs.score) AS riesgo_score
        FROM productos p
        JOIN principios_activos_cum pa ON pa.expediente = p.expediente
        LEFT JOIN match_principio_activo m ON m.nombre_cum = {_NORM.format('pa.principioactivo')}
        LEFT JOIN risk_scores rs ON rs.principio_activo = m.nombre_vitales
        WHERE {_NORM.format('p.producto')} LIKE {_NORM.format('%s')}
           OR {_NORM.format('pa.principioactivo')} LIKE {_NORM.format('%s')}
        GROUP BY p.expediente
        ORDER BY max(rs.score) DESC NULLS LAST LIMIT %s
        """,
        (patron, patron, limite),
    )
    return filas, {"dataset": FUENTES["cum"], "herramienta": "buscar_medicamento", "registros": len(filas)}


def riesgo_medicamento(principio_activo: str):
    patron = f"%{principio_activo.strip()}%"
    filas = query(
        f"""
        SELECT principio_activo, mes, score, nivel, tendencia, factores, prob_ml
        FROM risk_scores
        WHERE {_NORM.format('principio_activo')} LIKE {_NORM.format('%s')}
        ORDER BY score DESC LIMIT 5
        """,
        (patron,),
    )
    return filas, {"dataset": FUENTES["score"], "herramienta": "riesgo_medicamento", "registros": len(filas)}


def historial_solicitudes(principio_activo: str, limite: int = 12):
    patron = f"%{principio_activo.strip()}%"
    filas = query(
        f"""
        SELECT fecha_autorizacion, tipo_solicitud, solicitante_importador,
               principio_activo_1, cantidad_solicitada
        FROM solicitudes
        WHERE {_NORM.format('principio_activo_1')} LIKE {_NORM.format('%s')}
        ORDER BY fecha_autorizacion DESC NULLS LAST LIMIT %s
        """,
        (patron, limite),
    )
    return filas, {"dataset": FUENTES["vitales"], "herramienta": "historial_solicitudes", "registros": len(filas)}


def precios_medicamento(expediente: int):
    regulados = query(
        "SELECT cum, medicamento, pmax_institucional, pmax_comercial_final, circular, fecha_inicio_vigencia "
        "FROM precios_regulados WHERE expediente = %s LIMIT 10",
        (expediente,),
    )
    historicos = query(
        "SELECT mes, tipo_reporte, precio_promedio FROM precios_mensuales "
        "WHERE expediente = %s ORDER BY mes DESC LIMIT 12",
        (expediente,),
    )
    resultado = {"precio_maximo_regulado_vigente": regulados, "historico_sismed_2017_2019": historicos}
    fuente = FUENTES["regulados"] if regulados else FUENTES["sismed"]
    return resultado, {"dataset": fuente, "herramienta": "precios_medicamento", "registros": len(regulados) + len(historicos)}


def alternativas(expediente: int):
    filas = query(
        f"""
        SELECT DISTINCT p2.expediente, p2.producto, p2.titular, p2.estadoregistro
        FROM principios_activos_cum pa1
        JOIN principios_activos_cum pa2
          ON ({_NORM.format('pa2.principioactivo')} = {_NORM.format('pa1.principioactivo')}
              OR (pa1.atc IS NOT NULL AND left(pa2.atc, 5) = left(pa1.atc, 5)))
        JOIN productos p2 ON p2.expediente = pa2.expediente
        WHERE pa1.expediente = %s AND pa2.expediente <> %s
        LIMIT 8
        """,
        (expediente, expediente),
    )
    return filas, {"dataset": FUENTES["cum"], "herramienta": "alternativas", "registros": len(filas)}


def estadisticas_generales():
    fila = query(
        """
        SELECT
          (SELECT count(DISTINCT expediente) FROM productos) AS productos_vigentes,
          (SELECT count(*) FROM solicitudes) AS solicitudes_importacion,
          (SELECT count(*) FROM risk_scores WHERE nivel = 'critico') AS pas_riesgo_critico,
          (SELECT count(*) FROM risk_scores WHERE score >= 50) AS pas_riesgo_alto_o_mas,
          (SELECT max(mes) FROM risk_scores) AS mes_corte
        """
    )
    return fila, {"dataset": FUENTES["score"], "herramienta": "estadisticas_generales", "registros": 1}


# --- Definición OpenAI tools + despachador ---

ESQUEMAS = [
    {"type": "function", "function": {
        "name": "buscar_medicamento",
        "description": "Busca medicamentos en el catálogo CUM vigente por nombre comercial o principio activo. Devuelve expediente, producto, titular, estado y score de riesgo si existe.",
        "parameters": {"type": "object", "properties": {
            "nombre": {"type": "string", "description": "Nombre o principio activo a buscar"},
            "limite": {"type": "integer", "default": 5}},
            "required": ["nombre"]},
    }},
    {"type": "function", "function": {
        "name": "riesgo_medicamento",
        "description": "Score de riesgo de desabastecimiento (0-100) de un principio activo, con nivel, tendencia y factores.",
        "parameters": {"type": "object", "properties": {
            "principio_activo": {"type": "string"}}, "required": ["principio_activo"]},
    }},
    {"type": "function", "function": {
        "name": "historial_solicitudes",
        "description": "Últimas autorizaciones de importación excepcional (señal de escasez) de un principio activo.",
        "parameters": {"type": "object", "properties": {
            "principio_activo": {"type": "string"},
            "limite": {"type": "integer", "default": 12}}, "required": ["principio_activo"]},
    }},
    {"type": "function", "function": {
        "name": "precios_medicamento",
        "description": "Precios de un producto por expediente: precio máximo regulado vigente (Circular 19/2024) e histórico SISMED 2017-2019.",
        "parameters": {"type": "object", "properties": {
            "expediente": {"type": "integer"}}, "required": ["expediente"]},
    }},
    {"type": "function", "function": {
        "name": "alternativas",
        "description": "Medicamentos alternativos con el mismo principio activo o grupo ATC, por expediente.",
        "parameters": {"type": "object", "properties": {
            "expediente": {"type": "integer"}}, "required": ["expediente"]},
    }},
    {"type": "function", "function": {
        "name": "estadisticas_generales",
        "description": "Cifras generales de la plataforma: productos vigentes, solicitudes de importación, principios activos en riesgo.",
        "parameters": {"type": "object", "properties": {}},
    }},
]

_REGISTRO = {
    "buscar_medicamento": buscar_medicamento,
    "riesgo_medicamento": riesgo_medicamento,
    "historial_solicitudes": historial_solicitudes,
    "precios_medicamento": precios_medicamento,
    "alternativas": alternativas,
    "estadisticas_generales": estadisticas_generales,
}


def ejecutar(nombre: str, argumentos: dict):
    """Ejecuta una herramienta. Devuelve (json_para_el_llm, source)."""
    if nombre not in _REGISTRO:
        return json.dumps({"error": f"herramienta desconocida: {nombre}"}), None
    resultado, source = _REGISTRO[nombre](**argumentos)
    return json.dumps(resultado, ensure_ascii=False, default=str), source
