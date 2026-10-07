# Matriz de trazabilidad

Esta página demuestra que **todo conecta**. Cada historia de usuario se relaciona con su requisito, la estructura de datos o algoritmo que la resuelve, el endpoint que la expone, la tabla donde persiste, la pantalla donde se usa, el bloque de construcción ([Planeación](Planeacion.md)) y los repositorios que intervienen.

**Prioridad (MoSCoW):** **M** = Must · **S** = Should · **C** = Could.  
**Repos:** **F** = `Insumap-frontend` · **B** = `Insumap-backend` · **IA** = `Insumap-ai`.

| HU | R | Prioridad | Estructura / algoritmo | Endpoint(s) | Tabla(s) | Pantalla | Bloque | Repos |
|---|---|---|---|---|---|---|---|---|
| HU-20 Registrar cuenta | R20 | M | — | `POST /auth/registro` | `usuario`, `paciente`, `medico` | P02 | 2 | B, F |
| HU-21 Iniciar sesión | R21 | M | — | `POST /auth/login`, `GET /auth/me` | `usuario`, `refresh_token` | P01 | 2 | B, F |
| HU-22 Mantener / cerrar sesión | R22 | M | — | `POST /auth/refresh`, `POST /auth/logout` | `refresh_token` | P01, P09 | 2 | B, F |
| HU-23 Recuperar contraseña | R23 | S | — | `POST /auth/olvide-contrasena`, `/auth/restablecer-contrasena` | `reset_password_token` | P03 | 2 | B, F |
| HU-01 Mapa corporal 2D | R01 | M | E1 Matriz, E7 LRU | `GET /mapa` | `zona_macro` | P04 | 4 | B, F |
| HU-02 Cuadrícula de microzonas | R02 | M | E1 Matriz (+ proyección al redimensionar) | `GET /mapa`, `PUT /configuracion/cuadricula` | `paciente.tam_cuadricula` | P04, P09 | 4 | B, F |
| HU-03 Registrar inyección | R03 | M | E2 Tabla hash (búsqueda por ID) | `POST /inyecciones` | `inyeccion` | P04, P05 | 4 | B, F |
| HU-09 Almacenar hora | R09 | M | — (base de 5.1) | `POST /inyecciones` | `inyeccion.aplicada_en` | P05 | 4 | B |
| HU-07 Código de colores | R07 | M | Algoritmo 5.1 (umbrales) | `GET /mapa` | `config_parametros` | P04, P05 | 5 | B, F |
| HU-08 Bloqueo posterior | R08 | M | Algoritmo 5.1 (ratio = 0 → ROJO) | `POST /inyecciones` | `inyeccion` | P04 | 5 | B |
| HU-10 Calcular recuperación | R10 | M | Algoritmo 5.1 (`T_req`, `horas_restantes`) | `GET /mapa`, `GET /microzonas/{id}` | `zona_macro`, `config_parametros` | P05 | 5 | B, F |
| HU-04 Advertencia zona no recuperada | R04 | M | E2 + 5.1 (validación del color) | `POST /inyecciones` (409 `ZONA_NO_RECUPERADA`) | `inyeccion.advertencia_aceptada` | P05 | 5 | B, F |
| HU-05 Deshacer último registro | R05 | M | **E3 Pila** | `POST /inyecciones/deshacer` | `inyeccion.estado` | P05 (toast), P06 | 6 | B, F |
| HU-06 Restaurar estado | R06 | M | E3 Pila (`AccionRegistro.ultimo_uso_previo`) | `POST /inyecciones/deshacer` | `inyeccion.ultimo_uso_previo` | P04 | 6 | B, F |
| HU-17 Guardar historial | R17 | M | **E5 Lista doble** | `POST /inyecciones` | `inyeccion` | — | 6 | B |
| HU-18 Consultar historial | R18 | M | E5 Lista doble (paginación por cursor) | `GET /historial` | `inyeccion` | P06 | 6 | B, F |
| HU-11 Sugerir punto óptimo | R11 | M | **E4 Max-heap**, E6 Grafo, 5.2 | `GET /sugerencias` | `config_parametros` | P04 | 7 | B, F |
| HU-12 Penalizar sobreuso | R12 | S | 5.2 (`exceso`) + E2 `uso_macro` | `GET /sugerencias` | `inyeccion` (30 d) | P04 | 7 | B, F |
| HU-13 Priorizar olvidadas | R13 | S | 5.2 (`β·olvidada`) | `GET /sugerencias` | `inyeccion` | P04 | 7 | B, F |
| HU-28 Asistente: dónde aplicar | R28 | M | Tools → E4 (sugerencia) + `describir_ubicacion` | `POST /asistente/mensajes` | `mensaje_asistente` | P08 | 8 | IA, B, F |
| HU-29 Asistente: entender rotación | R29 | S | Tools → mapa / historial | `POST /asistente/mensajes` | `mensaje_asistente` | P08 | 8 | IA, B, F |
| HU-30 Respuestas seguras | R30 | M | Guardrails | `POST /asistente/mensajes` | `mensaje_asistente.bloqueado_por_guardrail` | P08 | 8 | IA |
| HU-14 Configurar cronograma | R14 | S | E4 Min-heap (programación) | `GET/PUT /cronograma` | `cronograma_dosis`, `recordatorio` | P07 | 9 | B, F |
| HU-15 Enviar recordatorios | R15 | S | **E4 Min-heap** + tick, 5.4 | `POST /push/suscripciones`, `/internal/recordatorios/tick` | `recordatorio`, `suscripcion_push` | P07 (push) | 9 | B, F |
| HU-16 Gestionar recordatorio | R16 | S | E4 Min-heap indexado (`actualizar_prioridad`) | `POST /recordatorios/{id}/posponer\|confirmar` | `recordatorio` | P07 → P04 | 9 | B, F |
| HU-24 Vincular médico | R24 | S | — | `POST /vinculos/codigos`, `POST /vinculos`, `GET /vinculos` | `codigo_vinculo`, `vinculo_medico_paciente` | P09, P10 | 10 | B, F |
| HU-25 Médico ve mapa | R25 | S | E1, E7 (reutiliza el `EstadoPaciente`) | `GET /medico/pacientes/{paciente_id}/mapa` | `vinculo_medico_paciente` | P11 | 10 | B, F |
| HU-26 Médico ve / exporta historial | R26 | S | E5 | `GET /medico/pacientes/{paciente_id}/historial[/exportar]` | `inyeccion` | P11 | 10 | B, F |
| HU-27 Revocar médico | R27 | S | — | `DELETE /vinculos/{id}` | `vinculo_medico_paciente.revocado_en` | P09 | 10 | B, F |
| HU-19 Exportar historial | R19 | S | E5 (recorrido cronológico) | `GET /historial/exportar` | `inyeccion` | P06 | 11 | B, F |

## Cobertura por estructura de datos

| Estructura | HU que la usan |
|---|---|
| E1 Matriz | HU-01, HU-02, HU-25 |
| E2 Tabla hash | HU-03, HU-04, HU-12 (+ base de E6, E7 y del heap indexado) |
| E3 Pila | HU-05, HU-06 |
| E4 Montículo (max) | HU-11, HU-12, HU-13, HU-28 |
| E4 Montículo (min, indexado) | HU-14, HU-15, HU-16 |
| E5 Lista doble | HU-17, HU-18, HU-19, HU-26 |
| E6 Grafo | HU-11 |
| E7 LRU | HU-01, HU-07, HU-25 (RNF-02) |

## Cobertura por requerimiento no funcional

| RNF | Dónde se atiende |
|---|---|
| RNF-01, RNF-05, RNF-06, RNF-13 | `Insumap-frontend` (P01–P11) |
| RNF-02 | E7 LRU + índice `(paciente_id, aplicada_en)` |
| RNF-03, RNF-04 | `core/security.py`, dependencia `requiere_vinculo()` en las rutas `/medico/*` |
| RNF-07 | cron externo + UptimeRobot |
| RNF-08 | CI en los 3 repositorios |
| RNF-10, RNF-11 | Guardrails y límites del [Módulo IA](Modulo-IA.md); avisos en P02/P09 |

**Regla de mantenimiento:** toda HU, endpoint, tabla o pantalla nueva **debe** agregarse a esta matriz en el mismo PR que la introduce (ver la Definition of Done en [Planeación](Planeacion.md)).
