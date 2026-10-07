# Insumap - Backend

API REST de **Insumap**, aplicación web *mobile first* para la rotación de zonas de inyección de insulina.

Usa FastAPI, PostgreSQL y **estructuras de datos implementadas a mano** (matriz, tabla hash, pila, montículos, lista doble, grafo y caché LRU).

- 📚 Documentación del proyecto: [`docs/`](docs/README.md)
- 🤖 Guía para colaboradores y agentes: [`AGENTS.md`](AGENTS.md)

## Inicio rápido

Requisitos: [uv](https://docs.astral.sh/uv/) y Docker o Podman.

```bash
uv sync
docker compose up -d db          # o: podman compose up -d db
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
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
