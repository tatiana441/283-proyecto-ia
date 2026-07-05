"""Tests del score compuesto de riesgo (fórmula interpretable)."""

import json

import pandas as pd
import yaml

from src.common import REPO_ROOT
from src.features.build_features import construir_panel
from src.inference import calcular_scores


def _panel_dos_pas():
    """GAMMA: activo y creciente. DELTA: una sola solicitud hace más de un año."""
    meses = [f"2024-{m:02d}" for m in range(1, 13)] + [f"2025-{m:02d}" for m in range(1, 7)]
    filas = []
    for i, mes in enumerate(meses):
        if i >= 12:  # GAMMA: 3 solicitudes/mes los últimos 6 meses
            for j in range(3):
                filas.append(("GAMMA", mes, "URGENCIA CLINICA", f"IPS {j}", 10))
    filas.append(("DELTA", "2024-02", "VITAL NO DISPONIBLE", "IPS X", 5))
    return pd.DataFrame(filas, columns=[
        "principio_activo_1", "mes_autorizacion", "tipo_solicitud",
        "solicitante_importador", "cantidad_solicitada_num",
    ])


def test_pesos_suman_uno():
    with open(REPO_ROOT / "config" / "risk_model_params.yaml", encoding="utf-8") as f:
        params = yaml.safe_load(f)
    assert abs(sum(params["pesos"].values()) - 1.0) < 1e-9


def test_score_en_rango_y_ordenado():
    scores = calcular_scores(construir_panel(_panel_dos_pas()))
    assert scores["score"].between(0, 100).all()
    porpa = scores.set_index("principio_activo")["score"]
    assert porpa["GAMMA"] > porpa["DELTA"], "el PA activo y creciente debe puntuar más alto"


def test_niveles_y_factores():
    scores = calcular_scores(construir_panel(_panel_dos_pas()))
    assert scores["nivel"].isin(["bajo", "medio", "alto", "critico"]).all()
    factores = json.loads(scores.iloc[0]["factores"])
    for clave in ["frecuencia", "tendencia", "recencia", "amplitud", "urgencia", "pesos"]:
        assert clave in factores
