"""Ranking de riesgo de desabastecimiento."""

from fastapi import APIRouter, Query

from src.api.db import query
from src.api.schemas import Riesgo

router = APIRouter(prefix="/api/riesgo", tags=["riesgo"])


@router.get("/top", response_model=list[Riesgo])
def top(n: int = Query(20, le=100), nivel: str | None = None):
    condicion = "WHERE nivel = %s" if nivel else ""
    params = (nivel, n) if nivel else (n,)
    return query(
        f"""
        SELECT principio_activo, mes, score, nivel, tendencia, factores
        FROM risk_scores {condicion}
        ORDER BY score DESC LIMIT %s
        """,
        params,
    )
