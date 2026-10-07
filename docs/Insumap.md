# Insumap

## Problema
Los pacientes con diabetes dependientes de insulina se aplican inyecciones varias veces al día para regular su glucosa. Para que el tratamiento sea efectivo, los médicos piden **rotar constantemente** las zonas de aplicación (abdomen, muslos, brazos y glúteos). En la práctica, los pacientes terminan inyectándose una y otra vez en los mismos puntos. Eso favorece alteraciones del tejido (lipohipertrofia) y una absorción irregular de la insulina.

## Solución
Insumap es una **aplicación web mobile first, instalable en el celular como PWA**, que elimina la necesidad de memorizar dónde fue la última inyección:

1. **Mapa corporal 2D** dividido en 4 zonas macro y en una cuadrícula configurable de microzonas.
2. **Cálculo de recuperación** de cada microzona según la zona, el tiempo transcurrido y la frecuencia de uso, con un **código de colores** rojo, amarillo y verde.
3. **Sugerencia del punto óptimo** con estructuras de datos propias (montículo de prioridad, grafo de vecindad), que penaliza las zonas sobreutilizadas y prioriza las olvidadas.
4. **Recordatorios** de dosis por notificación push.
5. **Historial** exportable para el médico, quien también puede **vincularse** y consultar la rotación del paciente.
6. **Asistente IA** que explica en lenguaje natural dónde queda la zona sugerida y por qué, sin dar consejos de dosis.

## Objetivos
- **General:** facilitar la rotación correcta de las zonas de inyección de insulina mediante una aplicación web que visualice, calcule y sugiera el punto óptimo de aplicación.
- **Específicos:**
  1. Modelar el cuerpo y sus microzonas con estructuras de datos eficientes, implementadas desde cero en Python.
  2. Implementar algoritmos de recuperación y de sugerencia con complejidad analizada y probada.
  3. Persistir de forma segura el historial clínico de aplicaciones en PostgreSQL.
  4. Construir una interfaz mobile first, accesible e instalable en TypeScript.
  5. Integrar un asistente basado en LLM, económico y seguro, que mejore la comprensión del paciente.

## Alcance
| Incluido | Fuera de alcance |
|---|---|
| Web PWA mobile first, mapa 2D, roles paciente y médico, recordatorios push, export PDF/Excel/CSV, asistente IA | App nativa, mapa 3D (mejora futura), visión por computador, recomendaciones de dosis, integración con glucómetros |

## Usuarios y roles
| Rol | Puede |
|---|---|
| **Paciente** | Registrar y deshacer inyecciones, ver el mapa y las sugerencias, configurar recordatorios, consultar y exportar el historial, usar el asistente, vincular o revocar médicos |
| **Médico** | Vincularse con un código del paciente y consultar en **solo lectura** su mapa y su historial (y exportarlo) |

> **Aviso:** Insumap es un proyecto académico de apoyo a la rotación. No es un dispositivo médico ni sustituye la indicación del médico tratante. Los parámetros de recuperación deben ser validados por un profesional de la salud.

Ver: [Arquitectura](Arquitectura.md) · [Estructuras de datos y algoritmos](Estructuras-de-datos-y-algoritmos.md) · [Planeación](Planeacion.md)
