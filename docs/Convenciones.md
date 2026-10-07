# Convenciones del equipo

> La guía completa para colaboradores y agentes está en [AGENTS.md](../AGENTS.md).

## Git y GitHub
- **GitHub Flow:** `main` siempre se puede desplegar. Se trabaja en ramas `tipo/HU-xx-descripcion-corta`, p. ej. `feat/HU-05-deshacer`.
- **Commits:** formato **`titulo: descripción`**, en español. El título es el área o tipo de cambio: `dominio: implementa el montículo indexado`, `api: agrega exportar historial`, `fix: corrige la paginación`, `tests: cubre deshacer`, `docs: actualiza el modelo de datos`. Un commit por cambio lógico.
- **PR:** título con la HU, descripción con "qué / cómo probar / capturas (si hay UI)", **1 aprobación** y CI en verde. Se usa *squash merge*.
- **Issues:** una por HU, con las etiquetas `repo:frontend|backend|ai` y `prioridad:must|should|could`.

## Código
| | Python (backend, ai) | TypeScript (frontend) |
|---|---|---|
| Estilo | `ruff format` + `ruff check` | Prettier + ESLint |
| Tipos | `mypy --strict` en `domain/` | `tsc --noEmit` (strict) |
| Nombres | `snake_case`; clases `PascalCase` | `camelCase`; componentes `PascalCase` |
| Idioma | **Todo el código en inglés** (identificadores, tablas, rutas, JSON, enums, códigos de error, comentarios, tests). En español solo lo que ve el usuario y la documentación | Igual |
| Tests | `pytest` en `tests/domain/` y `tests/api/` | `*.test.tsx` junto al componente |

## Estructura mínima de cada repo
```text
README.md        # qué es, cómo correrlo local, variables, link a la documentación
.env.example
.github/workflows/ci.yml
docker-compose.yml   # solo backend: PostgreSQL local
```

## Contrato de API
- El backend es la fuente del contrato (`/openapi.json`). Los cambios que rompan compatibilidad requieren **versión** (`/api/v2`) o acuerdo en el sync semanal.
- El frontend regenera los tipos con `npm run gen:api`.

## Diagramas
- Se hacen en **draw.io**. El fuente `.drawio` y su exportación `.png` van en `docs/images/`, con el mismo nombre.
