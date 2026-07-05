"""Esquemas Pydantic de la API — espejo de frontend/src/types/medication.ts."""

from pydantic import BaseModel


class MedicamentoResumen(BaseModel):
    expediente: int
    producto: str | None = None
    titular: str | None = None
    estadoregistro: str | None = None
    principios_activos: list[str] = []
    atc: str | None = None
    riesgo_score: float | None = None
    riesgo_nivel: str | None = None


class Riesgo(BaseModel):
    principio_activo: str
    mes: str
    score: float
    nivel: str
    tendencia: str
    factores: dict


class StatsRespuesta(BaseModel):
    productos: int
    principios_activos: int
    solicitudes_vitales: int
    pas_con_score: int
    pas_riesgo_alto: int
    mes_corte_riesgo: str | None = None
    top_riesgo: list[Riesgo] = []
