"""Búsqueda y detalle de medicamentos."""

from fastapi import APIRouter, HTTPException, Query

from src.api.db import query, query_one
from src.api.schemas import MedicamentoResumen

router = APIRouter(prefix="/api/medicamentos", tags=["medicamentos"])

# normalización en SQL equivalente a integrate.normalize_text (unaccent + upper)
_NORM = "unaccent(upper({}))"


@router.get("", response_model=list[MedicamentoResumen])
def buscar(search: str = Query(..., min_length=2), limit: int = Query(20, le=100)):
    patron = f"%{search.strip()}%"
    filas = query(
        f"""
        SELECT p.expediente, max(p.producto) AS producto, max(p.titular) AS titular,
               max(p.estadoregistro) AS estadoregistro,
               array_agg(DISTINCT pa.principioactivo) AS principios_activos,
               max(pa.atc) AS atc,
               max(rs.score) AS riesgo_score
        FROM productos p
        JOIN principios_activos_cum pa ON pa.expediente = p.expediente
        LEFT JOIN match_principio_activo m ON m.nombre_cum = {_NORM.format('pa.principioactivo')}
        LEFT JOIN risk_scores rs ON rs.principio_activo = m.nombre_vitales
        WHERE {_NORM.format('p.producto')} LIKE {_NORM.format('%s')}
           OR {_NORM.format('pa.principioactivo')} LIKE {_NORM.format('%s')}
        GROUP BY p.expediente
        ORDER BY max(rs.score) DESC NULLS LAST, max(p.producto)
        LIMIT %s
        """,
        (patron, patron, limit),
    )
    for f in filas:
        f["riesgo_nivel"] = _nivel(f["riesgo_score"])
    return filas


def _nivel(score) -> str | None:
    if score is None:
        return None
    if score < 25:
        return "bajo"
    if score < 50:
        return "medio"
    if score < 75:
        return "alto"
    return "critico"


@router.get("/{expediente}")
def detalle(expediente: int):
    perfil = query_one(
        """
        SELECT p.expediente, max(p.producto) AS producto, max(p.titular) AS titular,
               max(p.registrosanitario) AS registrosanitario, max(p.estadoregistro) AS estadoregistro,
               max(p.fechaexpedicion) AS fechaexpedicion, max(p.fechavencimiento) AS fechavencimiento,
               array_agg(DISTINCT pa.principioactivo) AS principios_activos,
               array_agg(DISTINCT pa.atc) FILTER (WHERE pa.atc IS NOT NULL) AS atc,
               array_agg(DISTINCT pa.descripcionatc) FILTER (WHERE pa.descripcionatc IS NOT NULL) AS descripcion_atc
        FROM productos p
        JOIN principios_activos_cum pa ON pa.expediente = p.expediente
        WHERE p.expediente = %s
        GROUP BY p.expediente
        """,
        (expediente,),
    )
    if not perfil:
        raise HTTPException(404, "Expediente no encontrado en el catálogo CUM vigente")

    presentaciones = query(
        """
        SELECT cum_std, descripcioncomercial, formafarmaceutica, estadocum, unidad, cantidadcum
        FROM presentaciones WHERE expedientecum = %s ORDER BY cum_std LIMIT 50
        """,
        (expediente,),
    )

    riesgo = query_one(
        f"""
        SELECT rs.principio_activo, rs.mes, rs.score, rs.nivel, rs.tendencia, rs.factores
        FROM risk_scores rs
        JOIN match_principio_activo m ON m.nombre_vitales = rs.principio_activo
        JOIN principios_activos_cum pa ON m.nombre_cum = {_NORM.format('pa.principioactivo')}
        WHERE pa.expediente = %s
        ORDER BY rs.score DESC LIMIT 1
        """,
        (expediente,),
    )

    historial = query(
        f"""
        SELECT s.fecha_autorizacion, s.mes_autorizacion, s.tipo_solicitud,
               s.solicitante_importador, s.principio_activo_1, s.cantidad_solicitada
        FROM solicitudes s
        WHERE {_NORM.format('s.principio_activo_1')} IN (
            SELECT m.nombre_vitales FROM match_principio_activo m
            JOIN principios_activos_cum pa ON m.nombre_cum = {_NORM.format('pa.principioactivo')}
            WHERE pa.expediente = %s
        )
        ORDER BY s.fecha_autorizacion DESC NULLS LAST LIMIT 60
        """,
        (expediente,),
    )

    precios_regulados = query(
        "SELECT cum, medicamento, pmax_institucional, pmax_comercial_final, circular, fecha_inicio_vigencia "
        "FROM precios_regulados WHERE expediente = %s ORDER BY cum LIMIT 30",
        (expediente,),
    )
    serie_precios = query(
        "SELECT mes, tipo_reporte, precio_promedio, precio_minimo, precio_maximo, unidades "
        "FROM precios_mensuales WHERE expediente = %s ORDER BY mes, tipo_reporte",
        (expediente,),
    )

    alternativas = query(
        f"""
        SELECT DISTINCT p2.expediente, p2.producto, p2.titular, p2.estadoregistro
        FROM principios_activos_cum pa1
        JOIN principios_activos_cum pa2
          ON ({_NORM.format('pa2.principioactivo')} = {_NORM.format('pa1.principioactivo')}
              OR (pa1.atc IS NOT NULL AND left(pa2.atc, 5) = left(pa1.atc, 5)))
        JOIN productos p2 ON p2.expediente = pa2.expediente
        WHERE pa1.expediente = %s AND pa2.expediente <> %s
        LIMIT 10
        """,
        (expediente, expediente),
    )

    return {
        "perfil": perfil,
        "presentaciones": presentaciones,
        "riesgo": riesgo,
        "historial_solicitudes": historial,
        "precios": {
            "regulado_vigente": precios_regulados,
            "historico_sismed": serie_precios,
            "nota": "Serie SISMED 2017-2019 (histórico de referencia); regulado = Circular CNPMDM vigente",
        },
        "alternativas": alternativas,
    }
