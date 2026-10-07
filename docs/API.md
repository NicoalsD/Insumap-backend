# API REST (`Insumap-backend`)

- **Base:** `https://<backend>/api/v1`
- **Formato:** JSON, fechas en ISO-8601 con zona horaria.
- **Documentación viva:** Swagger UI en `/docs` y contrato en `/openapi.json`. El frontend genera sus tipos desde ese contrato.
- **Autenticación:** `Authorization: Bearer <access_token>` (JWT, 15 min). El *refresh token* viaja en la cookie `insumap_rt` (`HttpOnly; Secure; SameSite=None; Path=/api/v1/auth`).
- **Roles:** `P` = PACIENTE, `M` = MEDICO, `S` = servicio interno (`X-Service-Token`), `—` = público.

## Formato de error (todas las rutas)

```json
{ "error": { "codigo": "ZONA_NO_RECUPERADA", "mensaje": "La microzona ABD-I-1-1 está en ROJO.", "detalle": { "color": "ROJO", "horas_restantes": 96.0 } } }
```

| HTTP | `codigo` | Cuándo |
|---|---|---|
| 400 | `VALIDACION` | Cuerpo inválido (Pydantic) |
| 401 | `NO_AUTENTICADO` / `TOKEN_EXPIRADO` | Falta el token o está vencido; el frontend intenta `/auth/refresh` |
| 403 | `SIN_PERMISO` | El rol no corresponde o el médico no está vinculado al paciente |
| 404 | `NO_ENCONTRADO` | Recurso inexistente |
| 409 | `ZONA_NO_RECUPERADA`, `EMAIL_EN_USO`, `NADA_QUE_DESHACER` | Conflictos de negocio |
| 429 | `LIMITE_EXCEDIDO` | Rate limit (login, asistente) |

---

## 1. Autenticación: R20–R23 (HU-20 a HU-23)

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/auth/registro` | — | Crea un usuario PACIENTE o MEDICO con aceptación de términos y tratamiento de datos | R20 |
| POST | `/auth/login` | — | Devuelve `access_token` y fija la cookie de refresh. Máximo 5 intentos cada 15 min por IP y email | R21 |
| POST | `/auth/refresh` | cookie | Rota el refresh token y emite un nuevo access token | R22 |
| POST | `/auth/logout` | P/M | Revoca el refresh token y borra la cookie | R22 |
| POST | `/auth/olvide-contrasena` | — | Envía un email con un enlace (responde 202 aunque el email no exista) | R23 |
| POST | `/auth/restablecer-contrasena` | — | `{token, nueva_contrasena}`; revoca todas las sesiones | R23 |
| GET | `/auth/me` | P/M | Perfil del usuario actual y su rol | R21 |

```http
POST /api/v1/auth/login
{ "email": "ana@correo.com", "contrasena": "********" }

200 OK   Set-Cookie: insumap_rt=...; HttpOnly; Secure
{ "access_token": "eyJ...", "token_type": "bearer", "expira_en": 900,
  "usuario": { "id": "…", "nombre": "Ana", "rol": "PACIENTE" } }
```

## 2. Mapa y configuración: R01, R02, R07, R10

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/mapa` | P | Estado completo: zonas macro, cuadrícula y, por microzona, `color`, `ratio`, `horas_restantes`, `ultimo_uso` | R01, R02, R07, R10 |
| GET | `/microzonas/{microzona_id}` | P | Detalle de una microzona y sus últimas 5 aplicaciones | R07, R10 |
| PUT | `/configuracion/cuadricula` | P | `{ "tam": 2 \| 4 \| 6 }`; reproyecta el estado (E1) | R02 |

```json
GET /api/v1/mapa  →  200
{ "tam_cuadricula": 4, "generado_en": "2026-10-20T08:00:00-05:00",
  "zonas": [ { "macro": "ABD", "nombre": "Abdomen", "lados": [ { "lado": "I",
      "celdas": [ { "id": "ABD-I-1-1", "fila": 1, "columna": 1, "color": "ROJO",
                    "ratio": 0.11, "horas_restantes": 96.0, "ultimo_uso": "2026-10-19T20:00:00-05:00" } ] } ] } ] }
```

## 3. Inyecciones: R03–R06, R08, R09

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/inyecciones` | P | Registra la inyección. Devuelve 409 `ZONA_NO_RECUPERADA` si la zona no está en VERDE y `confirmar_no_recuperada` es `false` | R03, R04, R08, R09 |
| POST | `/inyecciones/deshacer` | P | Desapila el último registro (E3) y restaura el estado previo; 409 `NADA_QUE_DESHACER` si la pila está vacía | R05, R06 |

```json
POST /api/v1/inyecciones
{ "microzona_id": "MUS-I-1-2", "aplicada_en": "2026-10-20T08:05:00-05:00",
  "confirmar_no_recuperada": false, "origen": "SUGERENCIA", "recordatorio_id": null }

201 Created
{ "inyeccion": { "id": "…", "microzona_id": "MUS-I-1-2", "estado": "REGISTRADA" },
  "microzona": { "id": "MUS-I-1-2", "color": "ROJO", "ratio": 0.0, "horas_restantes": 124.8 },
  "puede_deshacer": true }
```

## 4. Sugerencias: R10–R13

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/sugerencias?k=3` | P | Top-k del max-heap con el desglose del score (para que el asistente pueda explicarlo) | R11, R12, R13 |

```json
{ "sugerencias": [
  { "microzona_id": "GLU-D-1-1", "score": 2.5, "color": "VERDE",
    "desglose": { "ratio": 2.0, "bono_olvidada": 0.5, "penalizacion_macro": 0.0, "penalizacion_vecindad": 0.0 } } ] }
```

## 5. Cronograma y recordatorios: R14–R16

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/cronograma` | P | Horas configuradas | R14 |
| PUT | `/cronograma` | P | `{ "dosis": [{ "hora": "07:00", "etiqueta": "Desayuno" }, …] }`, de 1 a 6 elementos; reprograma el min-heap | R14 |
| POST | `/push/suscripciones` | P/M | Guarda la `PushSubscription` del navegador | R15 |
| DELETE | `/push/suscripciones/{id}` | P/M | Elimina la suscripción del dispositivo | R15 |
| GET | `/recordatorios/proximos` | P | Próximos recordatorios (respaldo dentro de la app si no hay push) | R15 |
| POST | `/recordatorios/{id}/posponer` | P | `{ "minutos": 5..120 }`, actualiza la prioridad en el heap | R16 |
| POST | `/recordatorios/{id}/confirmar` | P | `{ "registrar": true }` → el frontend abre el mapa con la sugerencia preseleccionada | R16 |
| POST | `/internal/recordatorios/tick` | S (`CRON_TOKEN`) | Procesa el tope del min-heap y envía los push pendientes | R15 |

## 6. Historial y exportes: R17–R19

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| GET | `/historial?cursor=&limit=20&orden=desc&desde=&hasta=&macro=` | P | Paginación por cursor sobre la lista doble (E5) | R17, R18 |
| GET | `/historial/exportar?formato=pdf\|xlsx\|csv&desde=&hasta=` | P | Archivo con fecha, hora, microzona, macro y estado; 409 si está vacío | R19 |

## 7. Vínculo con el médico: R24–R27

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/vinculos/codigos` | P | Genera un código de 8 caracteres válido por 48 h | R24 |
| POST | `/vinculos` | M | `{ "codigo": "K7QX2M9A" }` crea el vínculo | R24 |
| GET | `/vinculos` | P/M | Paciente: sus médicos. Médico: sus pacientes | R24, R25 |
| DELETE | `/vinculos/{id}` | P | El paciente revoca el acceso | R27 |
| GET | `/medico/pacientes/{paciente_id}/mapa` | M (vinculado) | Mismo formato que `/mapa`, solo lectura | R25 |
| GET | `/medico/pacientes/{paciente_id}/historial` | M (vinculado) | Mismo formato que `/historial` | R26 |
| GET | `/medico/pacientes/{paciente_id}/historial/exportar` | M (vinculado) | Igual que el export del paciente | R26 |

## 8. Asistente IA: R28–R30

| Método | Ruta | Rol | Descripción | Req. |
|---|---|---|---|---|
| POST | `/asistente/mensajes` | P | `{ "mensaje": "¿Dónde me inyecto ahora?" }` → el backend reenvía a `Insumap-ai` con un token delegado de 2 min. Límite: 20 mensajes/hora | R28, R29, R30 |
| GET | `/asistente/mensajes?limit=30` | P | Conversación reciente | R28 |

```json
200 OK
{ "respuesta": "Te sugiero el glúteo derecho, cuadrante superior externo (GLU-D-1-1)…",
  "microzonas_referidas": ["GLU-D-1-1"], "fuente": "deepseek-chat", "degradado": false }
```

Si el LLM falla, se responde `degradado: true` con la sugerencia del algoritmo en texto plantilla (ver [Módulo IA](Modulo-IA.md)).

### Endpoints que usan las tools de `Insumap-ai`

El servicio IA llama **los mismos endpoints públicos** (`/mapa`, `/sugerencias`, `/historial`, `/microzonas/{id}`) con el **token delegado** del paciente. No existen rutas especiales con más privilegios.

Relacionadas: [Modelo de datos](Modelo-de-datos.md) · [Pantallas](Pantallas-mobile-first.md) · [Trazabilidad](Trazabilidad.md)
