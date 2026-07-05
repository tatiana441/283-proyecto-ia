"""Tests de integración de la API contra la base real (se omiten sin DATABASE_URL)."""

import os

import pytest

from src.common import load_env

load_env()
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"), reason="requiere DATABASE_URL (Supabase)"
)


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from src.api.main import app

    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_stats(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["productos"] > 9000
    assert data["pas_con_score"] > 400
    assert len(data["top_riesgo"]) == 5


def test_busqueda_tacrolimus(client):
    r = client.get("/api/medicamentos", params={"search": "tacrolimus"})
    assert r.status_code == 200
    resultados = r.json()
    assert len(resultados) > 0
    nombres = " ".join((m["producto"] or "") + " ".join(m["principios_activos"]) for m in resultados).upper()
    assert "TACROLIMUS" in nombres


def test_detalle_completo(client):
    expediente = client.get("/api/medicamentos", params={"search": "tacrolimus"}).json()[0]["expediente"]
    r = client.get(f"/api/medicamentos/{expediente}")
    assert r.status_code == 200
    data = r.json()
    for seccion in ["perfil", "presentaciones", "riesgo", "historial_solicitudes", "precios", "alternativas"]:
        assert seccion in data
    assert data["perfil"]["expediente"] == expediente


def test_riesgo_top_ordenado(client):
    r = client.get("/api/riesgo/top", params={"n": 10})
    assert r.status_code == 200
    top = r.json()
    assert len(top) == 10
    scores = [t["score"] for t in top]
    assert scores == sorted(scores, reverse=True)
    assert top[0]["factores"]  # JSONB llega como dict con la explicación
