"""Score compuesto de riesgo de desabastecimiento (0-100), interpretable por diseño.

Fórmula ponderada documentada en config/risk_model_params.yaml. Cada componente
está en [0, 1] y su contribución queda registrada en `factores` (JSONB) para que
el frontend y el asistente puedan explicar el porqué de cada score.
"""

import json

import pandas as pd
import psycopg
import yaml

from src.common import DATA_PROCESSED, REPO_ROOT, database_url
from src.features.build_features import construir_panel


def _params() -> dict:
    with open(REPO_ROOT / "config" / "risk_model_params.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calcular_scores(panel: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    """Calcula el score por principio activo en el último mes del panel."""
    params = params or _params()
    pesos = params["pesos"]
    niveles = params["niveles"]
    umbral_t = params["tendencia_umbral"]

    mes_actual = panel["mes"].max()
    df = panel[panel["mes"] == mes_actual].copy()

    # Componentes en [0, 1]
    df["c_frecuencia"] = df["sol_12m"].rank(pct=True)
    cambio_rel = (df["sol_3m"] - df["sol_3m_prev"]) / df["sol_3m_prev"].clip(lower=1)
    df["c_tendencia"] = (cambio_rel.clip(-1, 1) + 1) / 2
    df["c_recencia"] = (1 - df["recencia_meses"] / 12).clip(0, 1)
    df["c_amplitud"] = df["solicitantes_12m"].rank(pct=True)
    df["c_urgencia"] = df["pct_urgencia_6m"].clip(0, 1)

    df["score"] = (100 * (
        pesos["frecuencia"] * df["c_frecuencia"]
        + pesos["tendencia"] * df["c_tendencia"]
        + pesos["recencia"] * df["c_recencia"]
        + pesos["amplitud"] * df["c_amplitud"]
        + pesos["urgencia"] * df["c_urgencia"]
    )).round(1)

    df["nivel"] = pd.cut(
        df["score"],
        bins=[-1, niveles["bajo"], niveles["medio"], niveles["alto"], 101],
        labels=["bajo", "medio", "alto", "critico"],
    ).astype(str)

    df["tendencia"] = "estable"
    df.loc[cambio_rel > umbral_t, "tendencia"] = "subiendo"
    df.loc[cambio_rel < -umbral_t, "tendencia"] = "bajando"

    df["factores"] = df.apply(
        lambda r: json.dumps({
            "frecuencia": round(float(r["c_frecuencia"]), 3),
            "tendencia": round(float(r["c_tendencia"]), 3),
            "recencia": round(float(r["c_recencia"]), 3),
            "amplitud": round(float(r["c_amplitud"]), 3),
            "urgencia": round(float(r["c_urgencia"]), 3),
            "solicitudes_12m": int(r["sol_12m"]),
            "solicitudes_3m": int(r["sol_3m"]),
            "solicitantes_12m": int(r["solicitantes_12m"]),
            "meses_desde_ultima": int(r["recencia_meses"]),
            "pesos": pesos,
        }, ensure_ascii=False),
        axis=1,
    )

    out = df[["pa", "mes", "score", "nivel", "tendencia", "factores"]].rename(
        columns={"pa": "principio_activo"}
    )
    return out.sort_values("score", ascending=False).reset_index(drop=True)


def cargar_supabase(scores: pd.DataFrame) -> None:
    import io

    buf = io.StringIO()
    scores.to_csv(buf, index=False, header=False, na_rep="")
    buf.seek(0)
    with psycopg.connect(database_url(), connect_timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM risk_scores")
            with cur.copy(
                "COPY risk_scores (principio_activo, mes, score, nivel, tendencia, factores) "
                "FROM STDIN WITH (FORMAT csv, NULL '')"
            ) as copy:
                copy.write(buf.getvalue())
        conn.commit()
    print(f"[inference] risk_scores cargados: {len(scores):,}")


def main() -> None:
    solicitudes = pd.read_csv(DATA_PROCESSED / "vitales" / "solicitudes.csv")
    panel = construir_panel(solicitudes)
    scores = calcular_scores(panel)

    out = DATA_PROCESSED / "features"
    out.mkdir(parents=True, exist_ok=True)
    scores.to_csv(out / "risk_scores.csv", index=False, encoding="utf-8")

    print(f"[inference] mes de corte: {scores['mes'].iloc[0]}")
    print(scores[["principio_activo", "score", "nivel", "tendencia"]].head(10).to_string(index=False))
    cargar_supabase(scores)


if __name__ == "__main__":
    main()
