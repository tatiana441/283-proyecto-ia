# Changelog — MediWatch

Registro cronológico de versiones y cambios.

## [0.5.0] — 2026-07-12 · Robustez y validación

### Agregado
- **Guardia anti-falsos en el cruce fuzzy** (`integrate.py::_token_distintivo_difiere` + 4 tests): descarta cruces que solo difieren por número romano (Factor VIII vs XIII), isómero (interferón alfa vs beta) o prefijo (megestrol vs nomegestrol). Revisión manual de los 26 cruces por similitud → elimina 6 falsos, conserva 23 legítimos.
- **Línea base de contraste** en la evaluación: ordenar por sola frecuencia (persistencia) iguala el precision@20; el ranking se documenta como validación de señal, no como superioridad sobre reglas simples (`conclusiones.md`, `marco_metodologico.md`).
- **Aviso de uso responsable** en el panel del score (frontend): un puntaje alto no implica desabastecimiento inmediato ni justifica acumular.

### Corregido
- Etiquetas de las figuras del modelo: la ROC/matriz muestran el AUC del último corte (0,731), distinto del promedio de los 4 cortes (0,787) — aclarado para evitar confusión.
- Cobertura del cruce: 27% → **26%** de PAs tras descartar los 6 falsos (`reports/metricas_integracion.json`, propagado a la BD).

## [0.4.0] — 2026-07-05 · Día 4

### Agregado
- **Despliegue**: `deployments/docker/Dockerfile.api`, `frontend/Dockerfile` (build estático con args VITE_*), `.dockerignore` y guía paso a paso `docs/despliegue.md` (GitHub + Railway).
- **Automatización**: workflow `data-update-cron.yml` — re-ingesta semanal (lunes 3 a.m. Colombia) + recálculo de scores, con `workflow_dispatch` manual.
- **Documentación del jurado completa**: conclusiones, evaluación de impacto/ética, guía de validación para pares, architecture.md + diagrama PNG, `api_spec.json` (OpenAPI exportado), **informe_tecnico.pdf** y **manual_usuario.pdf**.
- **Notebooks 01/03/04/05** reproducibles (EDA, descriptivo, modelo con backtest, reportes automáticos).
- **RECURSOS/**: `Presentacion.pptx` (12 diapositivas con notas de orador) y `portada.png`.

### Corregido
- **Puente de integración**: ahora emite una fila por **cada variante CUM** del principio activo matcheado — productos enlazados a su score: 534 → **628** (la búsqueda de lidocaína ahora muestra el score 89,7).
- **Pipeline cron-safe**: DDL por tabla (solo se recrean las tablas con datos en la corrida), `chat_logs` y `risk_scores` nunca se tumban, SISMED se omite con gracia si el parquet no está (CI/cron).

## [0.3.0] — 2026-07-05 · Día 3

### Agregado
- **Asistente conversacional** (`src/agents/citizen_agent.py`): tool-calling vía OpenRouter con 6 herramientas de datos y trazabilidad `sources[]`; prompts versionados en `models/llm_rag/prompt_templates.json`; `POST /api/chat` con persistencia en `chat_logs`. Verificado con pregunta real (metotrexato: score 56,3, última autorización dic-2025, fuentes citadas).
- **Agente analista** (`src/agents/analyst_agent.py`): aiInsight determinista y explicable por medicamento + reporte automático de riesgo (`reports/reporte_riesgo_automatico.md`).
- **Bias tests** (`tests/bias_tests/`): invarianza al nombre, no supresión de huérfanos, no alarmismo sin evidencia, techo de la urgencia, distribución real no degenerada.
- **Frontend real**: Supabase Auth reemplaza a Clerk (login/registro propios, sesión reactiva); cliente API con adaptador a los tipos existentes; búsqueda y detalle con datos en vivo (perfil + riesgo con aiInsight + precios SISMED/regulados + historial + alternativas); página `/alto-riesgo` con el ranking; estadísticas reales en la landing; **ChatWidget** flotante con fuentes.
- `docs/marco_metodologico.md` (CRISP-ML(Q)). Build de producción del frontend en verde.

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
