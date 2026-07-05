"""Validación predictiva del riesgo: regresión logística con backtest temporal.

Label: el principio activo registra solicitudes de importación en los 3 meses
siguientes. Entrena solo con pasado y evalúa en meses posteriores al corte
(sin fuga temporal). Reporta AUC y precision@20 por corte, y exporta el modelo,
las métricas y las figuras para el jurado.
"""

import json
import pickle

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.common import DATA_PROCESSED, REPO_ROOT, REPORTS
from src.features.build_features import FEATURES_MODELO, agregar_label, construir_panel

FIGURAS = REPORTS / "figures"
MODELOS = REPO_ROOT / "models" / "predictive"


def _params() -> dict:
    with open(REPO_ROOT / "config" / "risk_model_params.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _mes_offset(mes: str, k: int) -> str:
    return str(pd.Period(mes, freq="M") + k)


def backtest(panel: pd.DataFrame, cortes: list[str], horizonte: int, k: int) -> tuple[list[dict], dict]:
    resultados = []
    ultimo = {}
    etiquetado = agregar_label(panel, horizonte).dropna(subset=["y"])
    etiquetado["y"] = etiquetado["y"].astype(int)

    for corte in cortes:
        # Entrenar con labels que solo usan información hasta el corte
        train = etiquetado[etiquetado["mes"] <= _mes_offset(corte, -horizonte)]
        test = etiquetado[(etiquetado["mes"] > corte) & (etiquetado["mes"] <= _mes_offset(corte, horizonte))]
        if train.empty or test.empty or test["y"].nunique() < 2:
            continue

        modelo = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced"),
        )
        modelo.fit(train[FEATURES_MODELO], train["y"])
        proba = modelo.predict_proba(test[FEATURES_MODELO])[:, 1]

        top_k = test.assign(proba=proba).nlargest(k, "proba")
        resultados.append({
            "corte": corte,
            "n_train": len(train),
            "n_test": len(test),
            "prevalencia_test": round(float(test["y"].mean()), 3),
            "auc": round(float(roc_auc_score(test["y"], proba)), 3),
            f"precision_at_{k}": round(float(top_k["y"].mean()), 3),
        })
        ultimo = {"test": test, "proba": proba, "modelo": modelo}

    return resultados, ultimo


def figuras_evaluacion(test: pd.DataFrame, proba, k: int) -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)

    # Matriz de confusión (umbral 0.5)
    cm = confusion_matrix(test["y"], (proba >= 0.5).astype(int))
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(cm, display_labels=["Sin solicitudes", "Con solicitudes"]).plot(ax=ax, colorbar=False)
    ax.set_title("Matriz de confusión — último corte del backtest")
    fig.tight_layout()
    fig.savefig(FIGURAS / "matriz_confusion.png", dpi=150)
    plt.close(fig)

    # Curva ROC
    fpr, tpr, _ = roc_curve(test["y"], proba)
    auc = roc_auc_score(test["y"], proba)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], "--", color="gray")
    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Tasa de verdaderos positivos")
    ax.set_title("Curva ROC — riesgo de desabastecimiento")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURAS / "roc.png", dpi=150)
    plt.close(fig)


def figuras_descriptivas(panel: pd.DataFrame) -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)

    # Distribuciones: serie mensual total + top principios activos
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    serie = panel.groupby("mes")["n_solicitudes"].sum()
    axes[0].plot(range(len(serie)), serie.values)
    ticks = range(0, len(serie), 12)
    axes[0].set_xticks(list(ticks))
    axes[0].set_xticklabels([serie.index[i] for i in ticks], rotation=45)
    axes[0].set_title("Solicitudes de importación por mes")
    axes[0].set_ylabel("Solicitudes")

    top = panel.groupby("pa")["n_solicitudes"].sum().nlargest(12).sort_values()
    axes[1].barh(top.index, top.values)
    axes[1].set_title("Top 12 principios activos por solicitudes")
    axes[1].tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(FIGURAS / "distribuciones.png", dpi=150)
    plt.close(fig)

    # Correlaciones entre features
    corr = panel[FEATURES_MODELO].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(corr)))
    ax.set_yticklabels(corr.columns, fontsize=8)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im)
    ax.set_title("Correlación entre features de riesgo")
    fig.tight_layout()
    fig.savefig(FIGURAS / "correlaciones.png", dpi=150)
    plt.close(fig)


def main() -> None:
    params = _params()
    horizonte = params["modelo"]["label_horizonte_meses"]
    k = params["modelo"]["precision_at_k"]

    solicitudes = pd.read_csv(DATA_PROCESSED / "vitales" / "solicitudes.csv")
    panel = construir_panel(solicitudes)
    figuras_descriptivas(panel)

    resultados, ultimo = backtest(panel, params["modelo"]["cortes_backtest"], horizonte, k)
    if not ultimo:
        raise RuntimeError("El backtest no produjo ningún corte evaluable")

    figuras_evaluacion(ultimo["test"], ultimo["proba"], k)

    # Modelo final: todo el histórico etiquetable
    etiquetado = agregar_label(panel, horizonte).dropna(subset=["y"])
    etiquetado["y"] = etiquetado["y"].astype(int)
    modelo_final = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    modelo_final.fit(etiquetado[FEATURES_MODELO], etiquetado["y"])

    MODELOS.mkdir(parents=True, exist_ok=True)
    with open(MODELOS / "modelo_riesgo.pkl", "wb") as f:
        pickle.dump({"modelo": modelo_final, "features": FEATURES_MODELO}, f)

    coefs = dict(zip(FEATURES_MODELO, modelo_final.named_steps["logisticregression"].coef_[0].round(3)))
    metricas = {
        "backtest": resultados,
        "auc_promedio": round(sum(r["auc"] for r in resultados) / len(resultados), 3),
        f"precision_at_{k}_promedio": round(sum(r[f"precision_at_{k}"] for r in resultados) / len(resultados), 3),
        "coeficientes": coefs,
        "features": FEATURES_MODELO,
        "horizonte_meses": horizonte,
    }
    with open(MODELOS / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)

    print(json.dumps(metricas, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
