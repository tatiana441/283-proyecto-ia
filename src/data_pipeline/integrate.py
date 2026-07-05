"""Integración CUM ↔ Vitales por principio activo normalizado.

Hallazgo del EDA: la columna IUM del CUM está 100% vacía (la API ni la expone),
así que no existe llave directa entre las dos bases. El cruce viable es por
principio activo, con match en cascada:

    (a) exacto sobre texto normalizado
    (b) fuzzy con rapidfuzz token_sort_ratio >= UMBRAL (90)
    (c) sin match (queda registrado — evidencia honesta del % de integración)

Produce la tabla puente `match_principio_activo` y las métricas de cruce.
"""

import json
import re
import unicodedata

import pandas as pd
from rapidfuzz import fuzz, process

from src.common import DATA_PROCESSED, REPORTS

UMBRAL_FUZZY = 90

# Concentraciones y unidades incrustadas en los nombres de Vitales
# (p. ej. "METOTREXATO 50MG/2ML SOLUCION INYECTABLE")
_RE_PARENTESIS = r"\([^)]*\)"
_RE_CONCENTRACION = (
    r"\b\d+([.,]\d+)?\s*(MCG|MG|UG|G|KG|UI|IU|MEQ|MMOL|ML|L|%)(\s*/\s*\d*([.,]\d+)?\s*(MCG|MG|UG|G|KG|UI|IU|MEQ|MMOL|ML|L|DOSIS|H))?\b"
)
_RE_NUMEROS_SUELTOS = r"\b\d+([.,]\d+)?\b"
_RE_SEPARADOR_COMBO = r"\s*\+\s*|\s*/\s*"


def normalize_text(texto) -> str | None:
    """Normaliza para comparación: mayúsculas, sin tildes, sin espacios dobles."""
    if texto is None or (isinstance(texto, float) and pd.isna(texto)) or pd.isna(texto):
        return None
    s = str(texto).strip().upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = " ".join(s.split())
    return s or None


def limpiar_nombre_pa(nombre: str | None) -> str | None:
    """Quita concentraciones, paréntesis y números del nombre de un principio activo.

    "METOTREXATO 50MG/2ML (SODICO)" -> "METOTREXATO"
    """
    s = normalize_text(nombre)
    if not s:
        return None
    s = re.sub(_RE_PARENTESIS, " ", s)
    s = re.sub(_RE_CONCENTRACION, " ", s)
    s = re.sub(_RE_NUMEROS_SUELTOS, " ", s)
    s = re.sub(r"[^A-ZÑ /+]", " ", s)
    s = " ".join(s.split())
    return s or None


def componentes_pa(nombre_limpio: str) -> list[str]:
    """Separa combinaciones ("LOPINAVIR + RITONAVIR" o "AMOXICILINA/CLAVULANATO") en componentes."""
    partes = re.split(_RE_SEPARADOR_COMBO, nombre_limpio)
    return [p.strip() for p in partes if p and len(p.strip()) > 3]


def _indice_cum(nombres_cum: list[str]) -> dict[str, set[str]]:
    """Índice {variante_limpia -> TODOS los nombres CUM normalizados que le corresponden}.

    Un mismo principio activo aparece en el CUM con múltiples redacciones
    ("LIDOCAINA CLORHIDRATO", "LIDOCAINA CLORHIDRATO (EQUIVALENTE A ...)");
    el puente debe cubrirlas todas para que cada producto encuentre su score.
    """
    indice: dict[str, set[str]] = {}
    for n in nombres_cum:
        nn = normalize_text(n)
        limpio = limpiar_nombre_pa(n)
        if not nn or not limpio:
            continue
        indice.setdefault(limpio, set()).add(nn)
        for comp in componentes_pa(limpio):
            indice.setdefault(comp, set()).add(nn)
    return indice


def match_principios_activos(nombres_vitales: list[str], nombres_cum: list[str]) -> pd.DataFrame:
    """Cascada exacto -> fuzzy -> por componente (combos) -> sin match.

    Devuelve la tabla puente con UNA FILA POR VARIANTE CUM del nombre matcheado,
    de modo que el join SQL cubra todas las redacciones del principio activo.
    """
    indice = _indice_cum(nombres_cum)
    universo = list(indice.keys())

    def buscar(candidato: str):
        if candidato in indice:
            return indice[candidato], "exacto", 100.0
        encontrado = process.extractOne(candidato, universo, scorer=fuzz.token_sort_ratio, score_cutoff=UMBRAL_FUZZY)
        if encontrado:
            return indice[encontrado[0]], "fuzzy", round(encontrado[1], 1)
        return None, None, None

    filas = []
    for original in nombres_vitales:
        nv = normalize_text(original)
        limpio = limpiar_nombre_pa(original)
        if not nv or not limpio:
            continue

        variantes, metodo, score = buscar(limpio)
        if metodo is None:
            for comp in componentes_pa(limpio):
                variantes, metodo, score = buscar(comp)
                if metodo is not None:
                    metodo = f"{metodo}_componente"
                    break

        if metodo is None:
            filas.append({"nombre_vitales": nv, "nombre_cum": None, "metodo": "sin_match", "score": None})
        else:
            for variante in sorted(variantes):
                filas.append({"nombre_vitales": nv, "nombre_cum": variante, "metodo": metodo, "score": score})

    return pd.DataFrame(filas).drop_duplicates(subset=["nombre_vitales", "nombre_cum"])


def run(vitales_base: pd.DataFrame, principios_cum: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta la integración y guarda tabla puente + métricas."""
    pa_vitales = pd.concat([
        vitales_base["principio_activo_1"],
        vitales_base.loc[~vitales_base["principio_activo_2"].isin(["NO APLICA"]), "principio_activo_2"],
    ]).dropna().unique().tolist()

    pa_cum = principios_cum["principioactivo"].dropna().unique().tolist()

    puente = match_principios_activos(pa_vitales, pa_cum)

    # Métricas por nombre único (el puente ahora trae varias variantes CUM por PA)
    unicos = puente.drop_duplicates(subset=["nombre_vitales"])
    total = len(unicos)
    por_metodo = unicos["metodo"].value_counts().to_dict()
    vitales_norm = vitales_base["principio_activo_1"].map(normalize_text)
    con_match = set(puente.loc[puente["metodo"] != "sin_match", "nombre_vitales"])
    filas_cruzan = vitales_norm.isin(con_match).mean()

    metricas = {
        "principios_activos_vitales": total,
        "por_metodo": por_metodo,
        "pct_con_match": round(100 * (total - por_metodo.get("sin_match", 0)) / total, 1),
        "pct_filas_solicitudes_cruzan": round(100 * float(filas_cruzan), 1),
        "umbral_fuzzy": UMBRAL_FUZZY,
    }

    out = DATA_PROCESSED / "integracion"
    out.mkdir(parents=True, exist_ok=True)
    puente.to_csv(out / "match_principio_activo.csv", index=False, encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    with open(REPORTS / "metricas_integracion.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)

    print(f"[integrate] {metricas}")
    return puente
