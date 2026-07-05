# Evaluación de impacto público, ética y mitigación de sesgos

## Valor público

| Usuario | Problema hoy | Qué le da MediWatch |
|---------|--------------|---------------------|
| Pacientes y cuidadores | No hay forma sencilla de saber si un medicamento escasea ni cuánto debería costar | Búsqueda simple, score explicado en lenguaje claro, precio techo legal vigente, asistente en español |
| IPS y farmacias | Compras reactivas ante desabastecimientos | Ranking de riesgo con tendencia para anticipar compras |
| MinSalud / INVIMA | Datos fragmentados en 4 sistemas | Vista integrada + señal priorizada de los principios activos críticos |

## Principios éticos aplicados

1. **Sin datos personales**: los 4 datasets son públicos; `solicitante_importador` identifica personas jurídicas. `chat_logs` guarda solo la conversación, protegida por RLS (cada usuario ve únicamente la suya).
2. **Sin consejo médico**: el system prompt del asistente prohíbe dosis y recomendaciones clínicas, y redirige a profesionales de la salud. Verificado por tests.
3. **Trazabilidad total**: cada respuesta del asistente cita dataset y número de registros (`sources[]`); cada score expone sus factores (`factores` JSONB); los precios siempre llevan fuente y fecha.
4. **Honestidad estadística**: las métricas de integración y del modelo están versionadas en el repo, incluidas las desfavorables.
5. **No alarmismo**: un medicamento sin señales muestra explícitamente "sin señales de escasez en los datos oficiales" en lugar de un score inventado.

## Sesgos identificados y mitigación (tests automatizados en `tests/bias_tests/`)

| Riesgo de sesgo | Mitigación | Test |
|-----------------|-----------|------|
| Penalizar medicamentos huérfanos (un solo solicitante) | El componente "amplitud" pesa solo 0,10 | `test_huerfano_un_solicitante_puede_ser_alto` |
| Alarmar sin evidencia (poca historia) | Recencia y frecuencia dominan; una solicitud vieja → nivel bajo/medio | `test_poca_historia_no_es_critico_por_defecto` |
| Sesgo por identidad del medicamento | El score depende solo del comportamiento de solicitudes | `test_invarianza_al_nombre` |
| Sobre-ponderar la urgencia clínica | Techo del 10% del score | `test_urgencia_influye_pero_no_domina` |
| Sistema degenerado (todo crítico o todo bajo) | Verificación sobre datos reales: <50% críticos, ≥3 niveles en uso | `test_distribucion_real_no_degenerada` |

## Riesgos residuales

- **Interpretación errónea del score** como diagnóstico de disponibilidad en farmacia: se mitiga con el texto explicativo (aiInsight) que aclara qué mide exactamente.
- **Datos de origen desactualizados o con errores** (p. ej. mojibake y outliers encontrados en SISMED): el pipeline los trata y documenta, pero la calidad final depende de la fuente oficial.
- **Dependencia de un LLM externo** para el chat: si OpenRouter falla, la app sigue funcionando (el chat degrada con mensaje claro; los datos no dependen del LLM).
