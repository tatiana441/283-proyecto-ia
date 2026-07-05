"""Orquestador del pipeline completo de MediWatch.

    python -m src.data_pipeline.run_all [--offline] [--skip-load]

Etapas: ingesta (SODA/fallback) -> limpieza (CUM, Vitales, precios) ->
integración fuzzy -> carga a Supabase. Reproducible con un solo comando.
"""

import sys
import time

from src.data_pipeline import clean_cum, clean_precios, clean_vitales, ingest, integrate, load_supabase


def main() -> None:
    offline = "--offline" in sys.argv
    skip_load = "--skip-load" in sys.argv
    t0 = time.time()

    print("=== 1/5 INGESTA ===")
    crudos = ingest.ingest_all(offline=offline)
    if "cum" not in crudos or "vitales" not in crudos:
        raise SystemExit("[run_all] ABORTADO: sin datos de CUM o Vitales (ni API ni fallback)")

    print("\n=== 2/5 LIMPIEZA CUM ===")
    tablas_cum = clean_cum.run(crudos["cum"])

    print("\n=== 3/5 LIMPIEZA VITALES ===")
    tablas_vit = clean_vitales.run(crudos["vitales"])

    print("\n=== 4/5 PRECIOS (SISMED + regulados) ===")
    precios_mensuales = clean_precios.limpiar_sismed()
    precios_regulados = None
    if "precios_regulados" in crudos:
        precios_regulados = clean_precios.limpiar_precios_regulados(crudos["precios_regulados"])

    print("\n=== 5/5 INTEGRACIÓN ===")
    puente = integrate.run(tablas_vit["base_limpia"], tablas_cum["principios_activos_cum"])

    if skip_load:
        print("\n[run_all] --skip-load: no se carga a Supabase")
    else:
        print("\n=== CARGA A SUPABASE ===")
        tablas = {
            "productos": tablas_cum["productos"],
            "presentaciones": tablas_cum["presentaciones"],
            "principios_activos_cum": tablas_cum["principios_activos_cum"],
            "medicamentos_vitales": tablas_vit["medicamentos_vitales"],
            "solicitudes": tablas_vit["solicitudes"],
            "diagnosticos": tablas_vit["diagnosticos"],
            "match_principio_activo": puente,
            "precios_mensuales": precios_mensuales,
            "precios_regulados": precios_regulados,
        }
        load_supabase.run(tablas)

    print(f"\n[run_all] pipeline completo en {time.time() - t0:,.0f} s")


if __name__ == "__main__":
    main()
