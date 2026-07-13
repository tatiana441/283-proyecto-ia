# Marco metodológico — CRISP-ML(Q)

MediWatch sigue el ciclo CRISP-ML(Q) (Cross-Industry Standard Process for Machine Learning with Quality assurance). Mapeo de cada fase a lo ejecutado:

## 1. Entendimiento del negocio y de los datos

- Problema público: desabastecimiento de medicamentos vitales en Colombia (ver `planteamiento_problema.md`).
- 4 datasets oficiales evaluados y verificados en vivo contra la API SODA (ver `fuentes_datos.md`).
- **Hallazgo clave del EDA**: la columna IUM del CUM está 100% vacía → no existe llave directa entre catálogo y señal de escasez; se diseñó integración difusa por principio activo.
- Decisión basada en datos sobre el histórico SISMED: se conserva porque es la única fuente de precio para el 46,2% del catálogo (63,3% de cobertura vs 29,9% del regulado).

## 2. Preparación de los datos

- Limpieza reproducible portada 1:1 de los notebooks de EDA del equipo (`notebooks/02_*`) a módulos probados (`src/data_pipeline/clean_*.py`): normalización de columnas, texto, fechas con sentinelas, deduplicación, validación ATC/CIE-10, banderas de calidad.
- SISMED: corrección de encoding, precios 0 → no reportado, winsorización p99.5, agregación Mes × Expediente × TipoReporte (3,7M → 724k filas).
- Integración en cascada: exacto → fuzzy (rapidfuzz token_sort_ratio ≥ 90) → por componente de combinaciones → sin match, con pre-limpieza de concentraciones y paréntesis. Métricas en `reports/metricas_integracion.json` (~27% de PAs, 32,4% de filas). El "sin match" restante refleja el fenómeno: los vitales no disponibles suelen carecer de registro vigente (medido: el 72% de los "sin match" no se parece a ningún nombre del CUM, umbral <75).
- **Validación manual del fuzzy + guardia anti-falsos.** Se revisaron los 26 matches por similitud uno a uno. Se detectaron 6 falsos positivos que rapidfuzz dejaba pasar por >90 aunque cambiaran la molécula (número romano: Factor VIII vs XI vs XIII; isómero/griega: interferón alfa vs beta; prefijo: megestrol vs NOmegestrol). Se añadió un guardia (`_token_distintivo_difiere` en `integrate.py`, cubierto por tests) que exige coincidencia en esos tokens distintivos; elimina los 6 y conserva las 23 variantes legítimas. Impacto acotado: el puente solo enriquece la ficha, no alimenta el score.
- Pipeline completo reproducible con un comando: `python -m src.data_pipeline.run_all`.

## 3. Ingeniería del modelo

- **Score compuesto interpretable 0-100** (requisito de explicabilidad): suma ponderada de 5 componentes — frecuencia (0,35), tendencia (0,25), recencia (0,20), amplitud de solicitantes (0,10), urgencia clínica (0,10) — documentados en `config/risk_model_params.yaml` y expuestos por registro en `risk_scores.factores` (JSONB).
- **Validación predictiva**: regresión logística (`class_weight=balanced`) sobre el panel PA × mes; label = "registra solicitudes en los 3 meses siguientes"; features construidas solo con información pasada (sin fuga temporal).

## 4. Evaluación

- Backtest temporal en 4 cortes (2024-06 → 2025-11): entrenar hasta el corte, probar en los 3 meses siguientes.
- Resultados: **AUC promedio 0,787 · precision@20 = 0,988** (`models/predictive/metrics.json`). Nota: el AUC de las figuras (`reports/figures/roc.png`, matriz) es el del **último corte** (2025-11, 0,731), no el promedio de los cuatro — son medidas distintas, no una contradicción.
- **Línea base de contraste:** ordenar por sola frecuencia de solicitudes 12m alcanza un precision@20 equivalente (y AUC comparable), porque la escasez es muy persistente. El modelo se interpreta como validación de que el ranking captura señal real (99% vs 17% de tasa base), no como superioridad sobre reglas simples. Un label más exigente (aumentos/entradas nuevas) queda como trabajo futuro.
- **Pruebas de equidad** (`tests/bias_tests/`): invarianza al nombre, no supresión de medicamentos huérfanos (un solo solicitante), no alarmismo con poca historia, techo de influencia de la urgencia, distribución real no degenerada.

## 5. Despliegue

- API FastAPI sobre Supabase (Postgres + RLS), asistente conversacional con tool-calling y trazabilidad (`sources[]`, prompts versionados en `models/llm_rag/`), frontend React.
- **Nota de arquitectura del agente**: el asistente implementa el mismo patrón que enseñan frameworks como LangChain/LangGraph (LLM que decide qué herramienta invocar, ejecuta consultas sobre datos externos y responde solo con el contexto recuperado), pero directamente sobre la API de OpenRouter. Se prefirió así porque el flujo es simple (una pasada de tool-calling, sin ciclos ni multi-agente), la trazabilidad queda explícita en el código (`sources[]` + `chat_logs`) y se evitan dependencias adicionales; LangGraph aportaría valor si el flujo creciera a grafos cíclicos o aprobación humana intermedia.
- Automatización: re-ingesta semanal desde datos.gov.co vía GitHub Actions (día 4).

## 6. Monitoreo y calidad (Q)

- 36+ tests (unitarios, integración, sesgo) ejecutados en CI en cada push.
- `Changelog.md` como registro de versiones; métricas de integración y del modelo versionadas en el repo.
- Limitaciones documentadas en `conclusiones.md` (día 4): SISMED histórico, cobertura del cruce, señal basada solo en importaciones excepcionales.
