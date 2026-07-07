"""Ingesta de datos abiertos desde la API SODA de datos.gov.co.

Descarga paginada ($limit/$offset con $order=:id) de los 3 datasets del proyecto.
Si la descarga falla y el dataset tiene fallback_csv configurado, usa el CSV
local (snapshot 2026-06-04) para que el pipeline nunca se quede sin datos.
"""

import os
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from src.common import DATA_RAW, REPO_ROOT, load_config

# La API expone slugs distintos a los encabezados del CSV de descarga manual.
# Se mapean aquí para que la limpieza reciba siempre los nombres estilo CSV.
VITALES_API_TO_CSV = {
    "fecha_de_autorizaci_n": "fecha_de_autorizacion",
    "concentraci_n_delmedicamento1": "concentracion_delmedicamento1",
    "concentraci_n_del_medicamento2": "concentracion_del_medicamento2",
    "forma_farmac_utica": "forma_farmaceutica",
    "nombre_comercial_": "nombre_comercial",
    "presentaci_n_comercial": "presentacion_comercial",
    "c_digo_diagnostico_cie_10": "codigo_diagnostico_cie_10",
}


def fetch_dataset(
    resource_id: str, base_url: str, page_size: int, timeout: int, reintentos: int = 3
) -> pd.DataFrame:
    """Descarga un dataset completo paginando la API SODA.

    datos.gov.co responde lento en horas pico: cada página se reintenta con
    espera progresiva antes de rendirse (el cron de madrugada lo necesita).
    """
    headers = {}
    token = os.environ.get("SODA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token

    frames, offset = [], 0
    while True:
        url = f"{base_url}/{resource_id}.json"
        params = {"$limit": page_size, "$offset": offset, "$order": ":id"}
        for intento in range(1, reintentos + 1):
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=timeout)
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                if intento == reintentos:
                    raise
                espera = 20 * intento
                print(
                    f"[ingest] {resource_id} offset={offset}: intento {intento} falló "
                    f"({type(e).__name__}); reintento en {espera}s"
                )
                time.sleep(espera)
        chunk = resp.json()
        if not chunk:
            break
        frames.append(pd.DataFrame(chunk))
        offset += page_size
        if len(chunk) < page_size:
            break
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def ingest_all(offline: bool = False) -> dict[str, pd.DataFrame]:
    """Ingesta los 3 datasets. Devuelve {nombre: DataFrame} y guarda copia en data/raw/."""
    cfg = load_config()
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    hoy = date.today().strftime("%Y%m%d")
    out: dict[str, pd.DataFrame] = {}

    for name, ds in cfg["datasets"].items():
        df = pd.DataFrame()
        fuente = None
        if not offline:
            try:
                df = fetch_dataset(ds["resource_id"], cfg["base_url"], cfg["page_size"], cfg["timeout_seconds"])
                fuente = f"SODA {ds['resource_id']}"
            except Exception as e:  # noqa: BLE001 — cualquier fallo de red cae al fallback
                print(f"[ingest] {name}: fallo SODA ({type(e).__name__}: {e}); intentando fallback CSV")

        if df.empty and ds.get("fallback_csv"):
            fb = (REPO_ROOT / ds["fallback_csv"]).resolve()
            if fb.exists():
                df = pd.read_csv(fb, encoding="utf-8", low_memory=False)
                fuente = f"CSV local {fb.name}"

        if df.empty:
            print(f"[ingest] {name}: SIN DATOS (ni API ni fallback). El pipeline continúa sin este dataset.")
            continue

        if name == "vitales":
            df = df.rename(columns=VITALES_API_TO_CSV)

        raw_path = DATA_RAW / f"{name}_{hoy}.csv"
        df.to_csv(raw_path, index=False, encoding="utf-8")
        print(f"[ingest] {name}: {len(df):,} filas desde {fuente} -> {raw_path.name}")
        out[name] = df

    return out


if __name__ == "__main__":
    ingest_all(offline="--offline" in sys.argv)
