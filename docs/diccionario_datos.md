# Diccionario de datos — variables del consolidado MediWatch

Variables seleccionadas del modelo de datos integrado (Supabase) y del panel de features del score de riesgo.

## Catálogo (fuente: CUM INVIMA `i7cb-raxc`)

| # | Variable | Tabla | Tipo | Descripción |
|---|----------|-------|------|-------------|
| 1 | `expediente` | productos | BIGINT | Identificador del producto ante INVIMA — **llave de integración con precios** |
| 2 | `producto` | productos | TEXT | Nombre comercial del producto |
| 3 | `estadoregistro` | productos | TEXT | Estado del registro sanitario (Vigente/…) |
| 4 | `cum_std` | presentaciones | TEXT | CUM estándar `expediente-consecutivo` (llave con precios regulados) |
| 5 | `principioactivo` | principios_activos_cum | TEXT | Principio activo — **llave difusa de integración con Vitales** |
| 6 | `atc` | principios_activos_cum | TEXT | Código ATC (clasificación anatómico-terapéutica); ATC-4 define alternativas |
| 7 | `formafarmaceutica` | presentaciones | TEXT | Forma farmacéutica de la presentación |

## Señal de escasez (fuente: Vitales No Disponibles `sdmr-tfmf`)

| # | Variable | Tabla | Tipo | Descripción |
|---|----------|-------|------|-------------|
| 8 | `fecha_autorizacion` | solicitudes | DATE | Fecha de la autorización de importación excepcional |
| 9 | `tipo_solicitud` | solicitudes | TEXT | Urgencia clínica / vital no disponible / … |
| 10 | `principio_activo_1` | solicitudes | TEXT | Principio activo solicitado |
| 11 | `cantidad_solicitada` | solicitudes | DOUBLE | Cantidad autorizada a importar |
| 12 | `codigo_diagnostico_cie10` | diagnosticos | TEXT | Diagnóstico CIE-10 asociado |

## Precios (fuentes: SISMED histórico + CNPMDM `nauz-qkjw`)

| # | Variable | Tabla | Tipo | Descripción |
|---|----------|-------|------|-------------|
| 13 | `precio_promedio` | precios_mensuales | DOUBLE | Precio promedio observado (SISMED, mes × expediente × canal, 2017-2019) |
| 14 | `tipo_reporte` | precios_mensuales | TEXT | VENTA / COMPRA / RECOBRO |
| 15 | `pmax_institucional` | precios_regulados | DOUBLE | Precio máximo de venta institucional vigente (Circular 19/2024) |
| 16 | `mercado_relevante` | precios_regulados | TEXT | Mercado relevante regulado por la CNPMDM |

## Features del score de riesgo (panel PA × mes, derivadas)

| # | Variable | Tipo | Descripción |
|---|----------|------|-------------|
| 17 | `sol_12m` | DOUBLE | Solicitudes de importación acumuladas 12 meses (frecuencia) |
| 18 | `tendencia_3m` | DOUBLE | Solicitudes del trimestre menos el trimestre anterior |
| 19 | `recencia_meses` | INT | Meses desde la última solicitud (99 = nunca) |
| 20 | `solicitantes_12m` | DOUBLE | Amplitud: solicitantes distintos acumulados 12 meses |

**Salida:** `risk_scores.score` (0–100, fórmula ponderada en `config/risk_model_params.yaml`), `nivel` (bajo/medio/alto/crítico), `tendencia` (subiendo/estable/bajando) y `factores` (JSONB con la contribución de cada componente — trazabilidad del score).
