# Conclusiones, limitaciones y próximos pasos

## Hallazgos principales

1. **Las autorizaciones de importación excepcional son una señal medible de escasez.** El dataset Medicamentos Vitales No Disponibles crece ~940 filas/mes y permite construir un score de riesgo con capacidad predictiva real: **AUC 0,787 y precision@20 de 0,988** en backtest temporal — de los 20 principios activos que el modelo señala, ~99% registran nuevas solicitudes en los 3 meses siguientes. Comparamos contra una **línea base de persistencia** (ordenar solo por frecuencia de solicitudes): obtiene un top-20 equivalente, lo que confirma que la escasez es **fuertemente persistente** mes a mes. Por eso presentamos el modelo como *validación de que el ranking captura señal real* (99% vs 17% de tasa base), no como un predictor que supere a reglas simples.

2. **No existe llave directa entre los datasets oficiales** (la columna IUM del CUM está 100% vacía y la API ni la expone). La integración por principio activo normalizado con cascada exacto → fuzzy → componentes logra cubrir ~26% de los nombres (32,4% de las solicitudes) — y el análisis del "sin match" reveló un hallazgo de fondo: **gran parte de los medicamentos vitales no disponibles no están en el CUM vigente precisamente porque carecen de registro sanitario activo en Colombia**. El bajo cruce no es (solo) un problema técnico: es el fenómeno de desabastecimiento en sí.

3. **El riesgo se concentra en medicamentos huérfanos** (EVINACUMAB, GOLODIRSEN, CASIMERSEN — enfermedades raras) y en algunos esenciales de uso masivo (lidocaína, score 89,7). Dos perfiles de problema público distintos que requieren respuestas distintas.

4. **La fragmentación de precios es severa**: el precio regulado vigente solo cubre el 30% del catálogo; sumando el histórico SISMED se llega al 63%, y aun así **el 37% de los productos vigentes no tiene ningún dato público de precio**.

## Limitaciones

- **SISMED es histórico (2017-2019)**: se presenta siempre etiquetado como referencia, nunca como precio actual. El precio vigente proviene de la Circular 19/2024.
- **La señal de riesgo depende de un solo dataset**: solicitudes de importación excepcional. Desabastecimientos que no pasan por ese trámite no se detectan.
- **Cobertura del cruce CUM↔Vitales de ~26%** de nombres (tras descartar 6 cruces falsos por número romano/isómero); el detalle de un producto sin match muestra el catálogo sin score (comportamiento correcto: no alarmar sin evidencia).
- El score se recalcula semanalmente (cron), no en tiempo real.
- 9,5k filas limitan modelos complejos: la regresión logística fue el techo razonable (XGBoost no aportó mejora que justificara perder interpretabilidad).
- **El poder predictivo es en gran parte persistencia.** Una línea base que ordena por frecuencia iguala el precision@20; el label ("¿habrá solicitudes en 3 meses?") es relativamente fácil para un principio activo ya activo. Un label más exigente —predecir *aumentos* o *entradas nuevas* a desabastecimiento— es trabajo futuro. El valor actual es priorizar de forma fiable una lista fragmentada, no un modelo sofisticado.
- **Validación manual del cruce difuso.** Se revisaron los 26 matches por similitud uno a uno; se detectaron y corrigieron 6 falsos positivos (nombres que solo se distinguen por un número romano o un isómero: Factor VIII/XI/XIII, interferón alfa/beta, megestrol/nomegestrol) con un guardia que exige coincidencia en esos tokens distintivos. Estos cruces solo afectaban el enlace de enriquecimiento CUM↔score, nunca el cálculo del score.

## Próximos pasos

1. **Memoria de largo plazo del asistente**: la BD ya tiene pgvector instalado; el diseño previsto es una tabla `memories` por usuario con recuperación semántica, más el resumen de `chat_logs` previos al iniciar sesión.
2. **Alertas por correo** al usuario cuando un medicamento seguido cambie de nivel de riesgo (la UI de suscripción ya existe).
3. **Incorporar el dataset de escasez de la OMS/FDA** como señal externa de contraste.
4. **Series SISMED actuales**: gestionar acceso al SISMED vigente (el público llega a 2019) para precios observados recientes.
5. **Mejorar el match** con un diccionario de sinónimos INN/DCI (nombres internacionales de principios activos).
