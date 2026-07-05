"""Tests del panel de features con casos sintéticos de resultado conocido."""

import pandas as pd

from src.features.build_features import agregar_label, construir_panel


def _solicitudes_sinteticas():
    """PA 'ALFA': solicitudes en 2024-01, 2024-02, 2024-04. PA 'BETA': solo 2024-01."""
    return pd.DataFrame({
        "principio_activo_1": ["ALFA", "ALFA", "ALFA", "ALFA", "BETA"],
        "mes_autorizacion": ["2024-01", "2024-02", "2024-02", "2024-04", "2024-01"],
        "tipo_solicitud": ["URGENCIA CLINICA", "VITAL NO DISPONIBLE", "URGENCIA CLINICA", "VITAL NO DISPONIBLE", "VITAL NO DISPONIBLE"],
        "solicitante_importador": ["IPS A", "IPS B", "IPS C", "IPS A", "IPS A"],
        "cantidad_solicitada_num": [10, 20, 5, 15, 8],
    })


def test_panel_conteos_y_malla_completa():
    panel = construir_panel(_solicitudes_sinteticas())
    # malla completa: 2 PAs x 4 meses (2024-01..2024-04)
    assert len(panel) == 8

    alfa = panel[panel["pa"] == "ALFA"].set_index("mes")
    assert alfa.loc["2024-01", "n_solicitudes"] == 1
    assert alfa.loc["2024-02", "n_solicitudes"] == 2
    assert alfa.loc["2024-03", "n_solicitudes"] == 0
    # rolling de 3 meses en abril = feb(2) + mar(0) + abr(1)
    assert alfa.loc["2024-04", "sol_3m"] == 3
    assert alfa.loc["2024-04", "sol_12m"] == 4


def test_recencia():
    panel = construir_panel(_solicitudes_sinteticas())
    beta = panel[panel["pa"] == "BETA"].set_index("mes")
    assert beta.loc["2024-01", "recencia_meses"] == 0
    assert beta.loc["2024-04", "recencia_meses"] == 3


def test_label_horizonte_3():
    panel = construir_panel(_solicitudes_sinteticas())
    etiquetado = agregar_label(panel, horizonte=3)
    alfa = etiquetado[etiquetado["pa"] == "ALFA"].set_index("mes")
    # en 2024-01, ALFA tiene solicitudes en feb (t+1) -> y=1
    assert alfa.loc["2024-01", "y"] == 1
    # los últimos 3 meses no tienen label completa
    assert pd.isna(alfa.loc["2024-04", "y"])
