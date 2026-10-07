# AGENTS.md: Insumap Backend

Guía para cualquier persona o agente de IA que trabaje en este repositorio. **Léela completa antes de cambiar código.**

## 1. Qué es Insumap

Aplicación web *mobile first* (PWA) que ayuda a pacientes con diabetes insulinodependientes a **rotar las zonas de inyección**:
- Divide el cuerpo en 4 zonas macro y en microzonas (cuadrícula 2×2, 4×4 o 6×6 por lado).
- Calcula la recuperación de cada microzona (rojo / amarillo / verde).
- Sugiere el punto óptimo para la siguiente dosis.
- Envía recordatorios.
- Comparte el historial con el médico.
- Incluye un asistente IA que explica dónde aplicarse.

Es un proyecto académico de la materia **Estructura de Datos**. Sus requisitos obligatorios son: Python + TypeScript, base de datos, IA y varios repositorios desplegables.

| Repositorio | Lenguaje | Rol |
|---|---|---|
| `Insumap-backend` (este) | Python | API REST, dominio, **estructuras de datos propias**, PostgreSQL |
| `Insumap-frontend` | TypeScript | PWA React + Vite, mapa corporal SVG |
| `Insumap-ai` (por crear) | Python | Asistente LLM (DeepSeek / Qwen) que llama a esta API con un token delegado |

Equipo: Nicolas Diaz · Drako Salazar · Nicolas Mora.

**La documentación funcional y técnica completa está en [`docs/`](docs/README.md).** Antes de implementar una funcionalidad, ubica su HU y su requisito en [`docs/Trazabilidad.md`](docs/Trazabilidad.md).

## 2. Reglas obligatorias

### 2.1 Idioma
| Qué | Idioma |
|---|---|
| **Todo el código**: identificadores, módulos, clases, funciones, variables, tablas y columnas de BD, rutas de la API, campos JSON, valores de enums, códigos de error, comentarios, docstrings, nombres de tests, logs | **Inglés** |
| **Lo que ve el usuario**: `message` de los errores, textos de emails, exportes (PDF/CSV/Excel), respuestas del asistente, descripciones y resúmenes de Swagger | **Español** |
| **Documentación** (`docs/`, README, este archivo) | **Español** |

Única excepción: los **códigos de microzona** (`ABD`, `MUS`, `BRA`, `GLU`, lado `I`/`D`, p. ej. `GLU-D-1-1`). Son datos que ve el usuario y están definidos en la documentación, así que no se traducen.

### 2.2 Commits
- Formato: **`titulo: descripción`**, en español, en minúsculas y en imperativo o presente. El título es el área o tipo de cambio.
  - `dominio: implementa el montículo indexado para recordatorios`
  - `api: agrega endpoint de exportar historial`
  - `docs: actualiza el modelo de datos`
  - `fix: corrige la paginación del historial`
  - `tests: cubre el flujo de deshacer`
- Un commit por cambio lógico. No mezcles refactor con funcionalidad.
- Trabaja en ramas (`feat/HU-05-deshacer`, `fix/...`) y abre PR hacia `main` con CI en verde y 1 aprobación.

### 2.3 Estructuras de datos (lo que se evalúa en la materia)
- Todas las estructuras de `app/domain/structures/` están **implementadas a mano**. **Prohibido** usar `heapq`, `collections.deque`, `OrderedDict`, `functools.lru_cache`, `bisect`, `queue` ni librerías externas como sustituto de la estructura. Las `list` y `dict` nativas solo se usan como almacenamiento primitivo (arreglos, valores).
- Cada estructura documenta la complejidad de sus operaciones en el docstring (`O(1)`, `O(log n)`, ...) y tiene sus pruebas en `tests/domain/`.
- El paquete `app/domain/` **no importa** FastAPI ni SQLAlchemy. Debe pasar `mypy --strict`.

| Id | Clase | Archivo | Uso |
|---|---|---|---|
| E1 | `Grid` | `grid.py` | Cuadrícula de microzonas; `project_cell` reproyecta al cambiar el tamaño |
| E2 | `HashTable` | `hash_table.py` | Índice `microzone_id → Microzone`, uso por macro, índices auxiliares |
| E3 | `Stack` | `stack.py` | Deshacer registros (`UndoAction` con la foto previa) |
| E4 | `Heap` / `IndexedHeap` | `heap.py` | Max-heap de sugerencias / min-heap de recordatorios |
| E5 | `DoublyLinkedList` | `doubly_linked_list.py` | Historial (paginación por cursor, exportes) |
| E6 | `Graph` | `graph.py` | Vecindad de microzonas (BFS radio 1) |
| E7 | `LRUCache` | `lru_cache.py` | Caché de `PatientState` por paciente |

### 2.4 Seguridad y datos de salud
- Nunca subas secretos. Las variables nuevas van en `.env.example` con un valor de ejemplo.
- Las rutas del médico **siempre** verifican el vínculo activo (dependencia `LinkedPatient`).
- El token delegado del asistente (`type=delegated`, `scope=assistant:read`) **solo** sirve en endpoints de lectura (`ReadingPatient`). Nunca lo aceptes en escrituras.
- No registres en los logs datos sensibles (emails completos, tokens, contenido de mensajes).
- Los parámetros clínicos (`algorithm_params`, `macro_zones.base_hours`) son **valores de ejemplo sin validación clínica**. No los presentes como recomendación médica.
- El asistente nunca da dosis ni diagnósticos (R30). Si tocas `assistant_service.py`, mantén el filtro `DOSE_PATTERN`.

## 3. Arquitectura del código

```text
app/
├── main.py                 # FastAPI app, CORS, errores, lifespan (seed + carga del min-heap + APScheduler)
├── core/                   # config (pydantic-settings), clock, errors, security (Argon2 + JWT), rate_limit
├── api/
│   ├── deps.py             # DbSession, CurrentUser, CurrentPatient, ReadingPatient, CurrentDoctor, LinkedPatient
│   ├── schemas.py          # Modelos Pydantic de request/response
│   └── v1/                 # Routers: auth, body_map, injections, history, reminders, doctor, assistant
├── services/               # Casos de uso; manejan la transacción y sincronizan PatientState
├── repositories/           # Consultas SQLAlchemy reutilizables
├── domain/
│   ├── structures/         # E1–E7 (a mano)
│   ├── algorithms/         # recovery (5.1), suggestion (5.2), scheduler (5.4)
│   ├── patient_state.py    # PatientState: agrupa las estructuras de un paciente
│   ├── models.py           # Microzone, Params, UndoAction, enums
│   └── location.py         # Descripción anatómica determinista (texto para el usuario)
└── db/                     # Base, tipos portables (UTCDateTime, JSON/JSONB), models, session, seed
alembic/                    # Migraciones
tests/domain/               # Pruebas de estructuras y algoritmos (incluye el ejemplo 5.3 de la doc)
tests/api/                  # Pruebas de API con SQLite en memoria y reloj congelado
docs/                       # Documentación del proyecto (español)
```

**Regla de dependencias:** `api → services → domain ← repositories`.

**Flujo de una escritura** (registrar o deshacer):
1. El servicio toma `state_service.lock`.
2. Obtiene el `PatientState` de la caché LRU.
3. Valida contra el dominio.
4. Escribe en la BD y hace `commit`.
5. Aplica el cambio al `PatientState` en memoria. Si algo falla, llama a `state_service.invalidate(patient_id)`.

La BD es siempre la fuente de verdad. La caché expira por TTL (`STATE_CACHE_TTL_SECONDS`) y al cambiar el tamaño de cuadrícula.

**Hora:** usa siempre `app.core.clock.now()` (UTC y con zona horaria), nunca `datetime.now()`. Las pruebas congelan el reloj. Las columnas de fecha usan `UTCDateTime`.

## 4. Convenciones de la API

- Prefijo `/api/v1`. Rutas y campos JSON en inglés y `snake_case`.
- Errores con el formato `{"error": {"code": "ENGLISH_CODE", "message": "Mensaje en español", "detail": {}}}`. Lánzalos con `AppError` o con los helpers de `app/core/errors.py`. La validación devuelve `400 VALIDATION_ERROR`.
- Cada endpoint lleva un `summary` en español y un docstring que cite su HU o requisito (por ejemplo `HU-05 / R05`).
- Colores: `RED` / `YELLOW` / `GREEN`. Estados de inyección: `REGISTERED` / `UNDONE`. Roles: `PATIENT` / `DOCTOR`.

| Recurso | Endpoints principales |
|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/token` (para Swagger), `/auth/refresh`, `/auth/logout`, `/auth/forgot-password`, `/auth/reset-password`, `GET /auth/me` |
| Mapa | `GET /map`, `GET /microzones/{microzone_id}`, `PUT /settings/grid`, `GET /suggestions` |
| Inyecciones | `POST /injections` (409 `MICROZONE_NOT_RECOVERED` sin `confirm_not_recovered`), `POST /injections/undo` |
| Historial | `GET /history` (cursor), `GET /history/export?format=pdf\|xlsx\|csv` |
| Recordatorios | `GET/PUT /schedule`, `GET /reminders/upcoming`, `POST /reminders/{id}/snooze\|confirm`, `POST/DELETE /push/subscriptions`, `POST /internal/reminders/tick` (header `X-Cron-Token`) |
| Médico | `POST /links/codes`, `POST/GET /links`, `DELETE /links/{id}`, `GET /doctor/patients/{patient_id}/map\|history\|history/export` |
| Asistente | `POST/GET /assistant/messages` (modo degradado si `AI_SERVICE_URL` está vacío) |

## 5. Comandos

```bash
uv sync                                   # instalar dependencias (Python 3.12)
docker compose up -d db                   # PostgreSQL local (o el comando podman de abajo)
cp .env.example .env
uv run alembic upgrade head               # aplicar migraciones
uv run uvicorn app.main:app --reload      # API en http://localhost:8000  → Swagger en /docs

uv run pytest                             # todas las pruebas (SQLite en memoria, no requiere BD)
uv run pytest --cov=app                   # cobertura (meta: ≥ 90 % en app/domain)
uv run ruff check app tests alembic && uv run ruff format app tests alembic
uv run mypy                               # tipos estrictos en app/domain

uv run alembic revision --autogenerate -m "describe change"   # nueva migración (requiere BD local)
```

Sin Docker Compose (por ejemplo, Podman):

```bash
podman run -d --name insumap-db -e POSTGRES_USER=insumap -e POSTGRES_PASSWORD=insumap \
  -e POSTGRES_DB=insumap -p 5432:5432 docker.io/library/postgres:16-alpine
```

**Probar con Swagger** (`http://localhost:8000/docs`):
1. Pulsa **Authorize** y usa `paciente@demo.insumap` / `Insumap123` (o `medico@demo.insumap`).
2. Los usuarios demo se crean al arrancar si `SEED_DEMO_USERS=true`.

## 6. Cómo agregar una funcionalidad (checklist)

1. Ubica la HU, el requisito y la fila de la [Trazabilidad](docs/Trazabilidad.md). Si es nueva, agrégala primero en `docs/`.
2. **Dominio:** si necesitas una estructura o un algoritmo, va en `app/domain/` con pruebas en `tests/domain/`.
3. **Modelo:** cambia `app/db/models.py` y genera la migración de Alembic. Revísala, no confíes ciegamente en el autogenerate.
4. **Servicio** en `app/services/`, **schema** en `app/api/schemas.py` y **router** en `app/api/v1/` (regístralo en `router.py` si es nuevo).
5. **Pruebas de API** en `tests/api/`. Cubre el caso feliz, los errores 4xx y los permisos por rol.
6. Ejecuta `ruff`, `mypy` y `pytest` en local.
7. Actualiza `docs/API.md`, `docs/Modelo-de-datos.md` y `docs/Trazabilidad.md` si cambiaron.
8. Haz un commit `titulo: descripción` por cambio lógico.

## 7. Variables de entorno

Están todas documentadas en [`.env.example`](.env.example). Las más importantes:

| Variable | Uso |
|---|---|
| `DATABASE_URL` | PostgreSQL (`postgresql+psycopg://...`). Las pruebas usan `sqlite://` |
| `JWT_SECRET`, `JWT_ACCESS_MINUTES`, `JWT_REFRESH_DAYS` | Tokens |
| `COOKIE_SECURE`, `COOKIE_SAMESITE`, `CORS_ORIGINS` | En producción (Vercel + Render): `true`, `none` y el dominio del frontend |
| `SCHEDULER_ENABLED`, `CRON_TOKEN` | Recordatorios (APScheduler interno y cron externo) |
| `VAPID_*` | Web Push |
| `AI_SERVICE_URL`, `AI_SERVICE_TOKEN` | Servicio `Insumap-ai` |
| `SEED_DEMO_USERS` | Usuarios demo; `false` en producción |

## 8. Despliegue (Render + Neon)

- **Build:** `uv sync --frozen`
- **Pre-deploy:** `uv run alembic upgrade head`
- **Start:** `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configura un cron externo (cron-job.org) que haga `POST /api/v1/internal/reminders/tick` cada minuto con el header `X-Cron-Token`. Así los recordatorios siguen funcionando aunque Render se duerma.
- El min-heap de recordatorios vive en memoria. Se asume **una sola instancia**; si se escala, mover el planificador a un worker dedicado.
