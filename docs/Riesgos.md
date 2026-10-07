# Riesgos

**Escala:** Probabilidad (P) y Impacto (I) de 1 (bajo) a 3 (alto). **Exposición = P × I.**

| ID | Riesgo | P | I | Exp. | Mitigación | Contingencia |
|---|---|---|---|---|---|---|
| RG-01 | **Tiempo** disponible para 3 personas | 3 | 3 | 9 | Backlog MoSCoW, orden por dependencias y corte del MVP definidos ([Planeación](Planeacion.md)); contrato primero para trabajar en paralelo | Pasar los Should a "trabajo futuro" en la presentación |
| RG-02 | **Web Push en iPhone** solo funciona con la PWA **instalada** (iOS 16.4+) | 3 | 2 | 6 | Banner de instalación, texto en P07 | Recordatorios dentro de la app (`/recordatorios/proximos`) y email |
| RG-03 | **Render free se duerme** tras inactividad y el tick de recordatorios se detiene | 3 | 2 | 6 | Cron externo (cron-job.org) a `/internal/recordatorios/tick` cada minuto | Instancia paga mínima durante la presentación |
| RG-04 | **Parámetros clínicos no validados** (tiempos de recuperación) | 3 | 2 | 6 | Configurables en `config_parametros` y marcados `validado_clinicamente=false`; aviso RNF-11 | Consultar a un profesional de enfermería o endocrinología y ajustar sin cambiar código |
| RG-05 | **LLM**: caída, latencia, cambio de precios o modelos | 2 | 2 | 4 | SDK compatible con OpenAI + proveedor de respaldo (Qwen) | Modo degradado: sugerencia del algoritmo con texto de plantilla |
| RG-06 | **LLM da consejos clínicos** o inventa zonas | 2 | 3 | 6 | Guardrails de entrada y salida, tools obligatorias, `describir_ubicacion` determinista, 30 frases de prueba | Bloquear y registrar; ajustar el prompt |
| RG-07 | **Integración entre 3 repos** (tipos o contratos desalineados) | 2 | 2 | 4 | `openapi.json` + tipos generados; sincronización de integración del equipo | Congelar el contrato antes de empezar cada bloque |
| RG-08 | **Bajo dominio de alguna tecnología** (FastAPI, PWA, push) | 2 | 2 | 4 | Spikes (pruebas rápidas) de 2 h antes de cada bloque; trabajo en pareja en tareas críticas | Simplificar (p. ej. *polling* en lugar de push) |
| RG-09 | **Fuga de datos de salud** | 1 | 3 | 3 | RNF-03/RNF-04, tests 403, sin datos sensibles en los logs ni en el LLM | Revocar tokens y rotar secretos |
| RG-10 | **Cuota gratuita de Neon/Vercel** agotada | 1 | 2 | 2 | Índices adecuados, caché LRU | Exportar la BD y migrar a otro plan gratuito |
| RG-11 | **Usabilidad del mapa con cuadrícula 6×6** en pantallas pequeñas | 2 | 2 | 4 | Zoom por zona macro, objetivos ≥ 44 px | 4×4 como máximo en móvil |

## Supuestos

- El docente acepta servicios en planes gratuitos y un LLM externo de bajo costo.
- Por ahora no habrá validación clínica formal; se documenta como limitación.
- Los usuarios de la demo son ficticios; no se cargan datos reales de pacientes.

Relacionadas: [Requerimientos no funcionales](Requerimientos-no-funcionales.md) · [Planeación](Planeacion.md)
