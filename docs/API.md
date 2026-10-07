# API REST (`Insumap-backend`)

- **Base:** `https://<backend>/api/v1`
- **Formato:** JSON, fechas en ISO-8601 con zona horaria (UTC).
- **Documentación viva:** Swagger UI en `/docs`, ReDoc en `/redoc` y contrato en `/openapi.json`. El frontend genera sus tipos desde ese contrato.
- **Autenticación:** `Authorization: Bearer <access_token>` (JWT, 15 min). El *refresh token* viaja en la cookie `insumap_rt` (`HttpOnly`, `Path=/api/v1/auth`; `Secure` y `SameSite=None` en producción).
- **Roles:** `P` = `PATIENT`, `M` = `DOCTOR`, `S` = servicio interno, `—` = público. `P*` = además acepta el **token delegado** del asistente (solo lectura).
- **Idioma:** rutas, campos, enums y códigos de error en inglés; `message` (lo que ve el usuario) en español. Ver [AGENTS.md](../AGENTS.md).

## Probar con Swagger

1. Levanta la API (`uv run uvicorn app.main:app --reload`) y abre `http://localhost:8000/docs`.
2. Pulsa **Authorize** e ingresa `paciente@demo.insumap` / `Insumap123`. El botón usa `POST /auth/token` (formulario OAuth2).
3. Prueba `GET /map`, `GET /suggestions`, `POST /injections` y `POST /injections/undo`.

## Formato de error (todas las rutas)

```json
{ "error": { "code": "MICROZONE_NOT_RECOVERED",
             "message": "La microzona ABD-I-1-1 aún no se ha recuperado. Confirma si deseas registrarla de todas formas.",
             "detail": { "color": "RED", "hours_remaining": 96.0, "suggested_microzone_id": "GLU-D-1-1" } } }
```

| HTTP | `code` | Cuándo |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Cuerpo o parámetros inválidos (`detail.errors` lista los campos) |
| 400 | `INVALID_MICROZONE`, `TERMS_NOT_ACCEPTED`, `INVALID_RESET_TOKEN`, `INVALID_LINK_CODE`, `DUPLICATED_DOSE_TIME`, `APPLIED_IN_FUTURE`, `INVALID_CURSOR` | Reglas de negocio |
| 401 | `NOT_AUTHENTICATED`, `TOKEN_EXPIRED`, `INVALID_TOKEN`, `INVALID_CREDENTIALS`, `INVALID_REFRESH`, `INVALID_CRON_TOKEN` | Sin token, token vencido o inválido; el frontend intenta `/auth/refresh` ante `TOKEN_EXPIRED` |
| 403 | `FORBIDDEN` | Rol incorrecto, médico no vinculado o token delegado en una escritura |
| 404 | `NOT_FOUND` | Recurso inexistente |
| 409 | `MICROZONE_NOT_RECOVERED`, `EMAIL_IN_USE`, `NOTHING_TO_UNDO`, `EMPTY_HISTORY`, `ALREADY_LINKED`, `REMINDER_CLOSED` | Conflictos de negocio |
| 429 | `RATE_LIMITED` | Límite de intentos de login (5 cada 15 min) o de mensajes al asistente (20/h) |

---

## 1. Autenticación: R20–R23 (HU-20 a HU-23)

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/auth/register` | — | Crea un usuario `PATIENT` o `DOCTOR` (requiere `accept_terms: true`) e inicia sesión | R20 |
| POST | `/auth/login` | — | JSON `{email, password}` → `access_token` + cookie de refresh | R21 |
| POST | `/auth/token` | — | Igual que `login`, en formato formulario OAuth2 (`username` = email). Lo usa Swagger | R21 |
| POST | `/auth/refresh` | cookie | Rota el refresh token y emite un nuevo access token | R22 |
| POST | `/auth/logout` | cookie | Revoca el refresh token y borra la cookie (204) | R22 |
| POST | `/auth/forgot-password` | — | Envía un enlace válido 30 min (responde 202 aunque el email no exista) | R23 |
| POST | `/auth/reset-password` | — | `{token, new_password}`; revoca todas las sesiones | R23 |
| GET | `/auth/me` | P/M | Usuario actual | R21 |

```http
POST /api/v1/auth/login
{ "email": "ana@correo.com", "password": "********" }

200 OK   Set-Cookie: insumap_rt=...; HttpOnly; Path=/api/v1/auth
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 900,
  "user": { "id": "…", "name": "Ana", "email": "ana@correo.com", "role": "PATIENT" } }
```

## 2. Mapa, microzonas y sugerencias: R01, R02, R07, R10–R13

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/map?macro=` | P* | Por cada microzona: `color`, `ratio`, `hours_remaining`, `last_used`, `uses_30d` | R01, R02, R07, R10 |
| GET | `/microzones/{microzone_id}` | P* | Estado de la microzona y sus últimas 5 aplicaciones | R07, R10 |
| PUT | `/settings/grid` | P | `{ "grid_size": 2 \| 4 \| 6 }`; reproyecta el historial (E1) y devuelve el mapa | R02 |
| GET | `/suggestions?k=3` | P* | Top-k del max-heap con el desglose del score | R11, R12, R13 |

```json
GET /api/v1/map  →  200
{ "grid_size": 4, "generated_at": "2026-10-20T13:00:00Z",
  "zones": [ { "macro": "ABD", "label": "Abdomen", "sides": [ { "side": "I",
      "cells": [ { "id": "ABD-I-1-1", "row": 1, "col": 1, "color": "RED", "ratio": 0.1111,
                   "hours_remaining": 96.0, "last_used": "2026-10-20T01:00:00Z", "uses_30d": 5 } ] } ] } ] }

GET /api/v1/suggestions?k=1  →  200
{ "suggestions": [ { "microzone_id": "GLU-D-1-1", "score": 2.5, "color": "GREEN",
    "breakdown": { "ratio": 2.0, "forgotten_bonus": 0.5, "overuse_penalty": 0.0, "neighbor_penalty": 0.0 } } ] }
```

## 3. Inyecciones: R03–R06, R08, R09

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/injections` | P | Registra la inyección. Responde **409 `MICROZONE_NOT_RECOVERED`** si la microzona no está en `GREEN` y `confirm_not_recovered` es `false` | R03, R04, R08, R09 |
| POST | `/injections/undo` | P | Desapila el último registro (E3) y restaura el estado previo; 409 `NOTHING_TO_UNDO` si la pila está vacía o pasaron más de 24 h | R05, R06 |

```json
POST /api/v1/injections
{ "microzone_id": "MUS-I-1-2", "applied_at": null, "confirm_not_recovered": false,
  "origin": "SUGGESTION", "reminder_id": null }

201 Created
{ "injection": { "id": "…", "microzone_id": "MUS-I-1-2", "macro": "MUS", "side": "I",
                 "applied_at": "…", "registered_at": "…", "status": "REGISTERED", "undone_at": null },
  "microzone": { "id": "MUS-I-1-2", "color": "RED", "ratio": 0.0, "hours_remaining": 124.8, "…": "…" },
  "can_undo": true }
```

`origin` ∈ `MAP` · `SUGGESTION` · `REMINDER` · `ASSISTANT`. Si viene `reminder_id`, el recordatorio queda `CONFIRMED` y enlazado a la inyección.

## 4. Historial y exportes: R17–R19

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/history?cursor=&limit=20&order=desc&macro=&date_from=&date_to=` | P | Paginación por cursor sobre la lista doble (E5). `next_cursor` es `null` en la última página | R17, R18 |
| GET | `/history/export?format=pdf\|xlsx\|csv&date_from=&date_to=` | P | Archivo con Fecha, Hora, Microzona, Zona macro, Lado y Estado (en la zona horaria del paciente); 409 `EMPTY_HISTORY` si no hay datos | R19 |

## 5. Cronograma, recordatorios y Web Push: R14–R16

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/schedule` | P | Horas configuradas y zona horaria del paciente | R14 |
| PUT | `/schedule` | P | `{ "doses": [{ "time": "07:00", "label": "Desayuno" }, …] }` (1 a 6, sin repetir); genera los recordatorios de las próximas 24 h en el min-heap | R14 |
| GET | `/reminders/upcoming` | P | Próximos recordatorios (respaldo dentro de la app si no hay push) | R15 |
| POST | `/reminders/{reminder_id}/snooze` | P | `{ "minutes": 5..120 }` → actualiza la prioridad en el min-heap (`update_priority`), estado `SNOOZED` | R16 |
| POST | `/reminders/{reminder_id}/confirm` | P | Estado `CONFIRMED`; devuelve `suggested_microzone_id` para abrir el registro | R16 |
| GET | `/push/vapid-public-key` | — | Llave pública VAPID para `pushManager.subscribe` | R15 |
| POST | `/push/subscriptions` | P/M | Guarda la `PushSubscription` del navegador (`endpoint`, `p256dh`, `auth`) | R15 |
| DELETE | `/push/subscriptions/{subscription_id}` | P/M | Elimina la suscripción | R15 |
| POST | `/internal/reminders/tick` | S (`X-Cron-Token`) | Crea los recordatorios de las próximas 24 h y envía los vencidos del min-heap | R15 |

Estados de recordatorio: `PENDING` → `SENT` → (`SNOOZED` → `SENT`)* → `CONFIRMED` (o `SKIPPED`).

## 6. Vínculo con el médico: R24–R27

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/links/codes` | P | Genera un código de 8 caracteres (sin 0/O/1/I), de un solo uso, válido 48 h | R24 |
| POST | `/links` | M | `{ "code": "K7QX2M9A" }` crea el vínculo (no distingue mayúsculas ni guiones) | R24 |
| GET | `/links` | P/M | Paciente: sus médicos. Médico: sus pacientes | R24, R25 |
| DELETE | `/links/{link_id}` | P | El paciente revoca el acceso (204) | R27 |
| GET | `/doctor/patients/{patient_id}/map` | M (vinculado) | Mismo formato que `/map`, solo lectura | R25 |
| GET | `/doctor/patients/{patient_id}/history` | M (vinculado) | Mismo formato que `/history` | R26 |
| GET | `/doctor/patients/{patient_id}/history/export` | M (vinculado) | Igual que el export del paciente | R26 |

## 7. Asistente IA: R28–R30

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/assistant/messages` | P | `{ "message": "¿Dónde me inyecto ahora?" }`. El backend reenvía a `Insumap-ai` (`POST {AI_SERVICE_URL}/chat`) con un token delegado de 2 min. Límite: 20 mensajes/hora | R28, R29, R30 |
| GET | `/assistant/messages?limit=30` | P | Conversación reciente (`USER` / `ASSISTANT`) | R28 |

```json
200 OK
{ "reply": "Te sugerimos aplicar la próxima dosis en Glúteo derecho, parte superior y hacia adentro (…) (GLU-D-1-1).",
  "referenced_microzones": ["GLU-D-1-1"], "source": "template", "degraded": true }
```

- **Modo degradado:** si `AI_SERVICE_URL` está vacío o el servicio falla, `degraded: true` y el texto se arma con el algoritmo de sugerencia y `describe_location` (ver [Módulo IA](Modulo-IA.md)).
- **Guardrail:** las preguntas de dosis reciben una respuesta fija (`source: "guardrail"`) sin llamar al LLM.

### Contrato con `Insumap-ai`

```json
POST {AI_SERVICE_URL}/chat        Header: X-Service-Token: <AI_SERVICE_TOKEN>
{ "patient_first_name": "Ana", "message": "¿Dónde me toca?",
  "history": [{ "role": "USER", "content": "…" }, { "role": "ASSISTANT", "content": "…" }],
  "delegated_token": "eyJ…" }

200 { "reply": "…", "referenced_microzones": ["GLU-D-1-1"], "provider": "deepseek", "model": "deepseek-chat",
      "input_tokens": 1500, "output_tokens": 180, "blocked_by_guardrail": false }
```

Las tools del servicio IA llaman a `GET /map`, `GET /suggestions`, `GET /history` y `GET /microzones/{id}` con `Authorization: Bearer <delegated_token>`. Ese token **no** sirve para escrituras (403).

## 8. Interno

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` (sin prefijo `/api/v1`) |

Relacionadas: [Modelo de datos](Modelo-de-datos.md) · [Pantallas](Pantallas-mobile-first.md) · [Trazabilidad](Trazabilidad.md)
