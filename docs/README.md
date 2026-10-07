# Insumap

**Aplicación web *mobile first* (PWA instalable en el celular)** para pacientes con diabetes dependientes de insulina. Ayuda a rotar las zonas de aplicación: calcula el tiempo de recuperación de cada microzona, muestra en un mapa corporal el punto óptimo para la siguiente dosis, envía recordatorios, permite compartir el historial con el médico e incluye un **asistente IA** que ayuda a ubicar la zona.

> Proyecto académico de la materia **Estructura de Datos**: Python + TypeScript, base de datos PostgreSQL e integración de IA (LLM).
>
> **Equipo:** Nicolas Diaz · Drako Salazar · Nicolas Mora

![Arquitectura de contenedores](images/c4-contenedores.png)

## Producción

- API desplegada en Render: https://insumap-backend.onrender.com · Swagger: https://insumap-backend.onrender.com/docs
- Base de datos: PostgreSQL en Neon (rama `production`)

## Repositorios

| Repo | Lenguaje | Contenido |
|---|---|---|
| `Insumap-frontend` | TypeScript | React + Vite + PWA, mapa corporal SVG |
| `Insumap-backend` | Python | FastAPI, estructuras de datos propias, PostgreSQL (esta documentación) |
| `Insumap-ai` *(por crear)* | Python | Asistente del paciente con DeepSeek / Qwen |

## Documentación

### Producto
- [Descripción del proyecto](Insumap.md): problema, objetivo, alcance y roles.
- [Historias de usuario](Historias-de-usuario.md): HU-01 a HU-30 con INVEST y Gherkin.
- [Requerimientos funcionales](Requerimientos-funcionales.md): R01 a R30.
- [Requerimientos no funcionales](Requerimientos-no-funcionales.md): RNF-01 a RNF-13.
- [Pantallas mobile first](Pantallas-mobile-first.md): wireframes P01 a P11.

### Técnico
- ⭐ [Estructuras de datos y algoritmos](Estructuras-de-datos-y-algoritmos.md): matriz, tabla hash, pila, montículos, lista doble, grafo y LRU; algoritmos de recuperación y sugerencia.
- [Arquitectura](Arquitectura.md): C4, capas, secuencias, despliegue y CI/CD.
- [Stack tecnológico](Stack-tecnologico.md)
- [Modelo de datos](Modelo-de-datos.md)
- [API REST](API.md)
- [Módulo IA](Modulo-IA.md)

### Gestión
- [Trazabilidad](Trazabilidad.md): HU → R → estructura → endpoint → tabla → pantalla → bloque → repositorio.
- [Planeación](Planeacion.md): equipo, MoSCoW, orden de construcción por dependencias, DoR/DoD.
- [Riesgos](Riesgos.md)
- [Convenciones](Convenciones.md)
- [Glosario](Glosario.md)
