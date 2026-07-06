# Guía de validación para pares

Cualquier persona puede reproducir y verificar los resultados de MediWatch. Requisitos: Python 3.12+, Node 20+, una BD Postgres (Supabase gratuito sirve).

## 1. Preparación (5 min)

```bash
git clone <repo> && cd <repo>
pip install -r requirements.txt
cp .env.example .env        # completar DATABASE_URL (y OPENROUTER_API_KEY para el chat)
```

## 2. Reproducir el pipeline completo (~3 min)

```bash
python -m src.data_pipeline.run_all
```

Qué verificar:
- Ingesta EN VIVO desde datos.gov.co (los conteos cambian con el tiempo; al cierre de este proyecto: CUM ~157k, Vitales ~10,5k, Precios regulados ~38,6k).
- `reports/metricas_integracion.json` → % de match por método (esperado ≈27,5% de PAs).
- Nota: sin el parquet SISMED local, el paso de precios históricos se omite con aviso — es el comportamiento diseñado.

## 3. Reproducir el modelo y sus métricas (~1 min)

```bash
python -m src.train
python -m src.inference
```

Qué verificar:
- `models/predictive/metrics.json`: AUC promedio ≈0,78 y precision@20 ≈0,99 en 4 cortes temporales (los valores exactos varían levemente al re-ingestar datos más nuevos).
- `reports/figures/`: matriz de confusión, ROC, distribuciones, correlaciones.
- El backtest es temporal (train ≤ corte, test en los 3 meses siguientes): revisar `src/train.py::backtest` para confirmar que no hay fuga.

## 4. Correr los tests (36+)

```bash
python -m pytest tests/ -v          # unit + integración + bias
python -m pytest tests/bias_tests -v  # solo equidad
```

### 4b. Tests E2E de interfaz (opt-in, con navegador real)

Siguiendo el patrón del curso (agent-browser de Vercel, módulo 13): un Chrome real
abre la app, hace login, navega al detalle de un medicamento y verifica que no haya
valores sin formatear (Infinity/NaN) ni desbordes de layout, dejando capturas como
evidencia en `reports/e2e/`.

```bash
npm install -g agent-browser        # una sola vez
# levantar la app: uvicorn src.api.main:app  +  npm run dev (frontend/)
# credenciales del usuario de prueba en .env: E2E_EMAIL y E2E_PASSWORD
E2E_BROWSER=1 python -m pytest tests/e2e_browser -v
```

Son opt-in (se saltan sin `E2E_BROWSER=1`) para que el CI no requiera navegador, y
las credenciales viven solo en `.env` — nunca en el repo.

## 5. Verificar la API y la trazabilidad

```bash
uvicorn src.api.main:app
```

- `http://localhost:8000/docs` → Swagger.
- `GET /api/medicamentos?search=lidocaina` → el primer resultado debe traer `riesgo_score` ≈ 89-90.
- `GET /api/riesgo/top?n=5` → dominado por medicamentos huérfanos; cada fila trae `factores` con la descomposición del score.
- `POST /api/chat` con `{"pregunta": "¿qué riesgo tiene el metotrexato?"}` → la respuesta debe citar fuentes (`sources[]` con dataset y nº de registros). Verificar contra los datos: `GET /api/medicamentos?search=metotrexato`.

## 6. Verificar el frontend

```bash
cd frontend && npm install && npm run dev
```

Flujo: registro → login → buscar "lidocaina" → ver score + factores + precios (etiquetados SISMED 2017-2019 vs Circular 19/2024) + historial → abrir el chat y validar que las fuentes citadas coinciden con lo mostrado.

## 7. Validaciones cruzadas contra las fuentes oficiales

- Conteo CUM: `https://www.datos.gov.co/resource/i7cb-raxc.json?$select=count(1)`
- Conteo Vitales: `https://www.datos.gov.co/resource/sdmr-tfmf.json?$select=count(1)`
- Un registro cualquiera del historial mostrado en la app puede buscarse directamente en el dataset Vitales por fecha y solicitante.
