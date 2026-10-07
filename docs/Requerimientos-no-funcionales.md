# Requerimientos no funcionales

Cada RNF tiene una **métrica verificable** y dice **cómo se prueba**.

| ID | Categoría | Requisito | Métrica / criterio | Cómo se verifica |
|---|---|---|---|---|
| **RNF-01** | Mobile first / rendimiento | El mapa corporal debe ser interactivo rápido en un celular de gama media con red 4G | LCP < 2.5 s y mapa interactivo < 2 s; bundle inicial < 250 KB gzip | Lighthouse móvil (≥ 85 en Performance) en CI o manual al cerrar cada bloque |
| **RNF-02** | Rendimiento backend | Las consultas frecuentes deben responder rápido | p95 < 300 ms en `/map` y `/suggestions` con la caché LRU caliente; < 800 ms en frío | Test de carga con `locust` (20 usuarios) antes de la entrega |
| **RNF-03** | Seguridad | Autenticación y autorización robustas | Contraseñas con Argon2id; JWT de 15 min; refresh rotativo en cookie `HttpOnly/Secure`; rate limit de login (5/15 min); CORS solo para el dominio del frontend; validación de rol y de **vínculo** en cada ruta del médico | Tests de API (401/403/429) y revisión con el checklist OWASP ASVS nivel 1 |
| **RNF-04** | Privacidad de datos de salud | Los datos de inyecciones son **datos sensibles** | Consentimiento explícito al registrarse (R20); acceso solo del titular y de los médicos que él autorice (R24, R27); HTTPS obligatorio; opción de borrar la cuenta; minimización de datos enviados al LLM (sin email ni identificadores). Si el equipo opera en Colombia, alinear con la **Ley 1581 de 2012** (habeas data, datos sensibles) — *por confirmar con el docente* | Revisión documental + test de que el médico no vinculado recibe 403 |
| **RNF-05** | Accesibilidad | Usable con daltonismo y lector de pantalla | WCAG 2.1 AA en contraste; estados con color **+ ícono + patrón**; objetivos táctiles ≥ 44 px; `aria-label` por microzona; vista alternativa en lista | axe DevTools sin errores críticos |
| **RNF-06** | Instalabilidad / PWA | Instalable y con uso offline básico | Manifest válido, service worker, mapa visible offline con el último estado, registros offline en cola | Lighthouse PWA + prueba en modo avión |
| **RNF-07** | Disponibilidad | Servicio disponible durante la evaluación | ≥ 99 % durante la presentación; recordatorios con un retraso máximo de 2 min | Monitor UptimeRobot (gratis) + log del tick |
| **RNF-08** | Mantenibilidad | Código probado y legible | Cobertura ≥ 90 % en `domain/` y ≥ 70 % global en el backend; lint y tipos sin errores; PR con review | Reporte de cobertura en CI |
| **RNF-09** | Observabilidad | Errores rastreables | Logs JSON con `request_id`; sin datos sensibles en los logs | Revisión de los logs de Render |
| **RNF-10** | Costo | Operación cercana a cero | Hosting en planes gratuitos o económicos; LLM con tope de tokens y rate limit; costo del LLM < 5 USD en todo el proyecto | Panel del proveedor LLM y `assistant_messages.*_tokens` |
| **RNF-11** | Seguridad del paciente / legal | La app no reemplaza el criterio médico | Aviso visible en el registro y en el Perfil: *"Insumap es un proyecto académico de apoyo a la rotación; no es un dispositivo médico ni sustituye la indicación de tu médico."* Parámetros clínicos marcados como no validados | Revisión de la UI |
| **RNF-12** | Compatibilidad | Navegadores objetivo | Chrome/Edge Android y escritorio (últimas 2 versiones), Safari iOS 16.4+ (push solo con la PWA instalada), Firefox | Prueba manual en la matriz de dispositivos del equipo |
| **RNF-13** | Usabilidad | Registrar una inyección debe ser rápido | ≤ 3 toques desde abrir la app (mapa → microzona → registrar) | Prueba con 5 usuarios (tiempo y errores) |

Relacionadas: [Requerimientos funcionales](Requerimientos-funcionales.md) · [Riesgos](Riesgos.md) · [Trazabilidad](Trazabilidad.md)
