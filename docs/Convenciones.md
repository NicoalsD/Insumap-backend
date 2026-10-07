# Convenciones del equipo

## Git y GitHub
- **GitHub Flow:** `main` siempre se puede desplegar. Se trabaja en ramas `tipo/HU-xx-descripcion-corta`, p. ej. `feat/HU-05-deshacer`.
- **Conventional Commits:** `feat(inyecciones): deshacer último registro (HU-05)`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`, `ci:`.
- **PR:** título con la HU, descripción con "qué / cómo probar / capturas (si hay UI)", **1 aprobación** y CI en verde. Se usa *squash merge*.
- **Issues:** una por HU, con las etiquetas `repo:frontend|backend|ai` y `prioridad:must|should|could`.

## Código
| | Python (backend, ai) | TypeScript (frontend) |
|---|---|---|
| Estilo | `ruff format` + `ruff check` | Prettier + ESLint |
| Tipos | `mypy --strict` en `domain/` | `tsc --noEmit` (strict) |
| Nombres | `snake_case`; clases `PascalCase` | `camelCase`; componentes `PascalCase` |
| Idioma | **Dominio en español** (`Microzona`, `inyeccion`, `Pila`) y técnica en inglés (`router`, `service`) | Igual |
| Tests | `pytest` en `tests/` espejo de `app/` | `*.test.tsx` junto al componente |

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
