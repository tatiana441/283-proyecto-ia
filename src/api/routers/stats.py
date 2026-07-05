"""Estadísticas para el dashboard/landing."""

from fastapi import APIRouter

from src.api.db import query, query_one
from src.api.schemas import StatsRespuesta

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsRespuesta)
def stats():
    conteos = query_one(
        """
        SELECT
          (SELECT count(DISTINCT expediente) FROM productos) AS productos,
          (SELECT count(DISTINCT principioactivo) FROM principios_activos_cum) AS principios_activos,
          (SELECT count(*) FROM solicitudes) AS solicitudes_vitales,
          (SELECT count(*) FROM risk_scores) AS pas_con_score,
          (SELECT count(*) FROM risk_scores WHERE score >= 50) AS pas_riesgo_alto,
          (SELECT max(mes) FROM risk_scores) AS mes_corte_riesgo
        """
    )
    top = query(
        "SELECT principio_activo, mes, score, nivel, tendencia, factores "
        "FROM risk_scores ORDER BY score DESC LIMIT 5"
    )
    return {**conteos, "top_riesgo": top}
