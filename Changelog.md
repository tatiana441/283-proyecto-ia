# Changelog — MediWatch

Registro cronológico de versiones y cambios.

## [0.2.0] — 2026-07-05 · Día 2

### Agregado
- `src/features/build_features.py`: panel mensual PA × mes (591 principios activos) con features sin fuga temporal (frecuencia 3/6/12m, tendencia, recencia, amplitud de solicitantes, % urgencia).
- `src/train.py`: validación predictiva con regresión logística y backtest temporal en 4 cortes — **AUC promedio 0,787 · precision@20 = 0,988**. Exporta modelo, `models/predictive/metrics.json` y figuras (`distribuciones`, `correlaciones`, `matriz_confusion`, `roc`).
- `src/inference.py`: score compuesto interpretable 0–100 (pesos en `config/risk_model_params.yaml`) con nivel, tendencia y factores explicables (JSONB); 591 scores cargados a `risk_scores`.
- API FastAPI (`src/api`): `GET /api/medicamentos?search=`, `GET /api/medicamentos/{expediente}` (perfil + riesgo + historial + precios + alternativas), `GET /api/riesgo/top`, `GET /api/stats`, `GET /health`. CORS configurable y búsqueda con `unaccent`.
- `docs/diccionario_datos.md` (20 variables del consolidado).
- 11 tests nuevos (features, score, API con TestClient contra Supabase) — 27 en total.

### Cambiado
- `integrate.py`: pre-limpieza de nombres de principios activos (concentraciones, paréntesis, números) y match por componentes en combinaciones ("X + Y"). Cruce sube de 22,2% → **27,5%** de PAs (32,4% de filas). El resto sin match se explica en gran parte porque los vitales no disponibles no tienen registro vigente en el CUM — hallazgo documentado.

## [0.1.0] — 2026-07-05 · Día 1

### Agregado
- Estructura del monorepo según el esqueleto del nivel avanzado del curso.
- `src/data_pipeline/ingest.py`: ingesta SODA paginada de 3 datasets de datos.gov.co (CUM `i7cb-raxc`, Vitales `sdmr-tfmf`, Precios Máximos `nauz-qkjw`) con fallback a CSV local.
- `src/data_pipeline/clean_cum.py` y `clean_vitales.py`: funciones de limpieza portadas 1:1 desde los notebooks del equipo (`notebooks/02_*`).
- `src/data_pipeline/clean_precios.py`: limpieza del SISMED compactado (parquet Spark del equipo, 3,7M filas) y de los precios máximos regulados; agregado mensual para carga.
- `src/data_pipeline/integrate.py`: integración CUM↔Vitales por principio activo normalizado con cascada exacto → fuzzy (rapidfuzz ≥ 90) → sin match; tabla puente y métricas de cruce.
- `src/data_pipeline/load_supabase.py`: DDL, carga masiva vía COPY (psycopg) y políticas RLS.
- `src/data_pipeline/run_all.py`: orquestador ingesta → limpieza → integración → carga.
- Tests unitarios y de integración (pytest) con fixtures de datos reales.
- Frontend React (prototipo del equipo) movido a `frontend/`.
- Notebooks de limpieza originales conservados como evidencia en `notebooks/`.
- Docs iniciales: planteamiento del problema y fuentes de datos.
