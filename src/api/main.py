"""MediWatch API — FastAPI sobre Supabase (Postgres).

    uvicorn src.api.main:app --reload
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import ensure_unaccent
from src.api.routers import medicamentos, riesgo, stats
from src.common import load_env


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_env()
    ensure_unaccent()
    yield


app = FastAPI(
    title="MediWatch API",
    description=(
        "Disponibilidad, riesgo de desabastecimiento y precios de medicamentos en Colombia. "
        "Datos abiertos: INVIMA (CUM, Vitales No Disponibles), SISMED y CNPMDM vía datos.gov.co."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

load_env()
origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(medicamentos.router)
app.include_router(riesgo.router)
app.include_router(stats.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "servicio": "mediwatch-api"}
