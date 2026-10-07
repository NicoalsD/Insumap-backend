# Glosario

| Término | Definición |
|---|---|
| **Zona macro** | Una de las 4 regiones corporales de aplicación: abdomen (`ABD`), muslos (`MUS`), brazos (`BRA`) y glúteos (`GLU`), cada una con lado izquierdo (`I`) y derecho (`D`). |
| **Microzona** | Celda de la cuadrícula `n×n` (2, 4 o 6) de una zona macro y lado. Se identifica como `ABD-I-2-3`. |
| **Ratio de recuperación** | `horas desde el último uso / tiempo requerido`. Determina el color. |
| **Rojo / Amarillo / Verde** | Estados de recuperación: no recuperada / parcialmente recuperada / recuperada. |
| **Zona olvidada** | Microzona sin uso durante 15 días o más (configurable). |
| **Sobreuso** | Zona macro cuyo uso en 30 días supera el promedio de las demás. |
| **Sugerencia / punto óptimo** | Microzona con mayor *score*, extraída del max-heap. |
| **`PatientState`** | Objeto en memoria que agrupa las estructuras de datos de un paciente. |
| **Token delegado** | JWT de corta duración que permite al servicio IA leer datos del paciente en su nombre. |
| **Lipodistrofia / lipohipertrofia** | Alteración del tejido graso por inyecciones repetidas en el mismo sitio; es la complicación que la rotación busca evitar. |
| **PWA** | *Progressive Web App*: web instalable, con service worker, uso offline y notificaciones push. |
| **Web Push / VAPID** | Estándar para enviar notificaciones a navegadores; VAPID identifica al servidor emisor. |
| **Function calling / tools** | Capacidad del LLM de solicitar la ejecución de funciones definidas por la app. |
| **Guardrail** | Regla que filtra la entrada o la salida del LLM para mantener la seguridad. |
| **MoSCoW** | Priorización Must / Should / Could / Won't. |
| **DoR / DoD** | Definition of Ready / Definition of Done. |
| **INVEST / Gherkin** | Criterios de calidad de una HU / lenguaje Dado-Cuando-Entonces para los criterios de aceptación. |
