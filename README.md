# Insumap - Backend

API REST de **Insumap**, aplicación web *mobile first* para la rotación de zonas de inyección de insulina.

Usa FastAPI, PostgreSQL y **estructuras de datos implementadas a mano** (matriz, tabla hash, pila, montículos, lista doble, grafo y caché LRU).

- Documentación del proyecto: [`docs/`](docs/README.md)
- Guía para colaboradores y agentes: [`AGENTS.md`](AGENTS.md)

## Producción

- API: https://insumap-backend.onrender.com
- Swagger: https://insumap-backend.onrender.com/docs (usuarios demo abajo)
- Base de datos: Neon, proyecto `raspy-sea-39960827`, rama `production`

## Inicio rápido

Requisitos: [uv](https://docs.astral.sh/uv/) y Docker o Podman.

```bash
uv sync
docker compose up -d db          # PostgreSQL local (o el comando podman de abajo)
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Sin Docker Compose (por ejemplo, Podman):

```bash
podman run -d --name insumap-db -e POSTGRES_USER=insumap -e POSTGRES_PASSWORD=insumap \
  -e POSTGRES_DB=insumap -p 5432:5432 docker.io/library/postgres:16-alpine
```

Abre **http://localhost:8000/docs** (Swagger), pulsa **Authorize** e ingresa:

| Usuario | Contraseña |
|---|---|
| `paciente@demo.insumap` | `Insumap123` |
| `medico@demo.insumap` | `Insumap123` |

Para probar:
1. Consulta `GET /api/v1/map` y `GET /api/v1/suggestions`.
2. Registra una inyección con `POST /api/v1/injections` y deshazla con `POST /api/v1/injections/undo`.

## Pruebas

```bash
uv run pytest            # SQLite en memoria, no necesita la BD
uv run pytest --cov=app
```

> Proyecto académico. No es un dispositivo médico. Los parámetros de recuperación son valores de ejemplo pendientes de validación clínica.
