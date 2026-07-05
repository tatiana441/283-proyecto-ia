# Conclusiones, limitaciones y próximos pasos

## Hallazgos principales

1. **Las autorizaciones de importación excepcional son una señal medible de escasez.** El dataset Medicamentos Vitales No Disponibles crece ~940 filas/mes y permite construir un score de riesgo con capacidad predictiva real: **AUC 0,787 y precision@20 de 0,988** en backtest temporal — de los 20 principios activos que el modelo señala, ~99% registran nuevas solicitudes en los 3 meses siguientes.

2. **No existe llave directa entre los datasets oficiales** (la columna IUM del CUM está 100% vacía y la API ni la expone). La integración por principio activo normalizado con cascada exacto → fuzzy → componentes logra cubrir el 27,5% de los nombres (32,4% de las solicitudes) — y el análisis del "sin match" reveló un hallazgo de fondo: **gran parte de los medicamentos vitales no disponibles no están en el CUM vigente precisamente porque carecen de registro sanitario activo en Colombia**. El bajo cruce no es (solo) un problema técnico: es el fenómeno de desabastecimiento en sí.

3. **El riesgo se concentra en medicamentos huérfanos** (EVINACUMAB, GOLODIRSEN, CASIMERSEN — enfermedades raras) y en algunos esenciales de uso masivo (lidocaína, score 89,7). Dos perfiles de problema público distintos que requieren respuestas distintas.

4. **La fragmentación de precios es severa**: el precio regulado vigente solo cubre el 30% del catálogo; sumando el histórico SISMED se llega al 63%, y aun así **el 37% de los productos vigentes no tiene ningún dato público de precio**.

## Limitaciones (declaradas honestamente)

- **SISMED es histórico (2017-2019)**: se presenta siempre etiquetado como referencia, nunca como precio actual. El precio vigente proviene de la Circular 19/2024.
- **La señal de riesgo depende de un solo dataset**: solicitudes de importación excepcional. Desabastecimientos que no pasan por ese trámite no se detectan.
- **Cobertura del cruce CUM↔Vitales del 27,5%** de nombres; el detalle de un producto sin match muestra el catálogo sin score (comportamiento correcto: no alarmar sin evidencia).
- El score se recalcula semanalmente (cron), no en tiempo real.
- 9,5k filas limitan modelos complejos: la regresión logística fue el techo razonable (XGBoost no aportó mejora que justificara perder interpretabilidad).

## Próximos pasos

1. **Memoria de largo plazo del asistente**: la BD ya tiene pgvector instalado; el diseño previsto es una tabla `memories` por usuario con recuperación semántica, más el resumen de `chat_logs` previos al iniciar sesión.
2. **Alertas por correo** al usuario cuando un medicamento seguido cambie de nivel de riesgo (la UI de suscripción ya existe).
3. **Incorporar el dataset de escasez de la OMS/FDA** como señal externa de contraste.
4. **Series SISMED actuales**: gestionar acceso al SISMED vigente (el público llega a 2019) para precios observados recientes.
5. **Mejorar el match** con un diccionario de sinónimos INN/DCI (nombres internacionales de principios activos).
