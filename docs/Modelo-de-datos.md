# Modelo de datos

La base de datos es **PostgreSQL** (Neon) y es la **fuente de verdad**. Las estructuras en memoria ([Estructuras de datos y algoritmos](Estructuras-de-datos-y-algoritmos.md)) se **construyen** desde estas tablas y cada escritura se persiste aquí en la misma transacción.

![Diagrama entidad-relación](images/modelo-er.png)

## Tablas

### Identidad y acceso

**`usuario`**: toda persona que inicia sesión (R20–R23).

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `uuid` | PK |
| `email` | `citext` | UNIQUE, NOT NULL |
| `password_hash` | `text` | NOT NULL (Argon2id) |
| `rol` | `enum('PACIENTE','MEDICO')` | NOT NULL |
| `nombre` | `varchar(120)` | NOT NULL |
| `activo` | `boolean` | default `true` |
| `creado_en` | `timestamptz` | default `now()` |

**`refresh_token`**: sesiones activas (R22).

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `uuid` | PK |
| `usuario_id` | `uuid` | FK → `usuario.id`, ON DELETE CASCADE |
| `token_hash` | `text` | UNIQUE (SHA-256 del token; nunca se guarda el token plano) |
| `expira_en` | `timestamptz` | NOT NULL |
| `revocado_en` | `timestamptz` | NULL = vigente |
| `creado_en` | `timestamptz` | |

**`reset_password_token`**: recuperación de contraseña (R23). Tiene `id`, `usuario_id` (FK), `token_hash` UNIQUE, `expira_en` (30 min) y `usado_en`.

**`paciente`**: perfil 1:1 con `usuario` cuando `rol = PACIENTE`.

| Columna | Tipo | Restricciones |
|---|---|---|
| `usuario_id` | `uuid` | PK, FK → `usuario.id` |
| `tam_cuadricula` | `smallint` | CHECK IN (2,4,6), default 4 (R02) |
| `zona_horaria` | `varchar(40)` | default `'America/Bogota'` |
| `fecha_nacimiento` | `date` | NULL |

**`medico`**: perfil 1:1 con `usuario` cuando `rol = MEDICO`. Tiene `usuario_id` (PK, FK), `registro_profesional` (`varchar(40)`) y `especialidad`.

### Vínculo médico–paciente (R24–R27)

**`codigo_vinculo`**: código de un solo uso que genera el paciente. Tiene `id`, `paciente_id` (FK), `codigo` (`char(8)` UNIQUE, alfanumérico sin caracteres ambiguos), `expira_en` (48 h) y `usado_en`.

**`vinculo_medico_paciente`**

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `uuid` | PK |
| `medico_id` | `uuid` | FK → `medico.usuario_id` |
| `paciente_id` | `uuid` | FK → `paciente.usuario_id` |
| `creado_en` | `timestamptz` | |
| `revocado_en` | `timestamptz` | NULL = activo |
| | | UNIQUE (`medico_id`, `paciente_id`) WHERE `revocado_en IS NULL` |

### Dominio clínico

**`zona_macro`**: catálogo fijo (*seed*) de las 4 zonas (R01).

| Columna | Tipo | Notas |
|---|---|---|
| `codigo` | `char(3)` | PK: `ABD`, `MUS`, `BRA`, `GLU` |
| `nombre` | `varchar(30)` | |
| `t_base_horas` | `numeric(5,1)` | **Parámetro clínico por validar** (ver algoritmo 5.1) |
| `orden_visual` | `smallint` | Orden en el mapa |

> **Microzona no es una tabla.** Es un concepto derivado de (`macro`, `lado`, `fila`, `columna`, `tam_cuadricula`) y se identifica con el ID `ABD-I-2-3`. Así, cambiar el tamaño de la cuadrícula no obliga a migrar filas: el historial se **proyecta** con escalado proporcional (ver E1).

**`inyeccion`**: el evento central (R03, R04, R08, R09, R17).

| Columna | Tipo | Restricciones / notas |
|---|---|---|
| `id` | `uuid` | PK |
| `paciente_id` | `uuid` | FK → `paciente.usuario_id`, INDEX |
| `macro` | `char(3)` | FK → `zona_macro.codigo` |
| `lado` | `char(1)` | CHECK IN ('I','D') |
| `fila`, `columna` | `smallint` | CHECK 1..`tam_cuadricula` |
| `tam_cuadricula` | `smallint` | Tamaño vigente al registrar |
| `microzona_id` | `varchar(12)` | Generada: `macro-lado-fila-columna`, INDEX |
| `aplicada_en` | `timestamptz` | NOT NULL; base del cálculo (R09) |
| `registrada_en` | `timestamptz` | default `now()` |
| `estado` | `enum('REGISTRADA','DESHECHA')` | default `REGISTRADA` (R17) |
| `deshecha_en` | `timestamptz` | NULL |
| `color_al_registrar` | `enum('ROJO','AMARILLO','VERDE')` | Auditoría de la advertencia (R04) |
| `advertencia_aceptada` | `boolean` | `true` si se registró en ROJO o AMARILLO |
| `ultimo_uso_previo` | `timestamptz` | Foto para **deshacer** (R06, pila E3) |
| `origen` | `enum('MAPA','SUGERENCIA','RECORDATORIO','ASISTENTE')` | Analítica de uso |

Índice compuesto: `(paciente_id, aplicada_en DESC) WHERE estado = 'REGISTRADA'`. Se usa para construir el `EstadoPaciente` y para paginar el historial.

**`config_parametros`**: parámetros del algoritmo (R10–R13).

| Columna | Tipo | Notas |
|---|---|---|
| `clave` | `varchar(40)` | PK: `alfa_frecuencia`, `umbral_amarillo`, `umbral_verde`, `ratio_max`, `ventana_uso_dias`, `dias_olvido`, `beta_olvido`, `gamma_sobreuso`, `delta_vecindad`, `horas_vecindad`, `top_k_sugerencias`, `ventana_deshacer_horas` |
| `valor` | `jsonb` | |
| `descripcion` | `text` | |
| `validado_clinicamente` | `boolean` | default `false` |
| `actualizado_en` | `timestamptz` | |

### Recordatorios (R14–R16)

**`cronograma_dosis`**: cada fila es una hora del día. La frecuencia diaria es el número de filas activas, entre 1 y 6 (HU-14).

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | `uuid` | PK |
| `paciente_id` | `uuid` | FK |
| `hora` | `time` | NOT NULL; UNIQUE (`paciente_id`, `hora`) |
| `etiqueta` | `varchar(40)` | p. ej. "Antes del desayuno" |
| `activo` | `boolean` | default `true` |

**`recordatorio`**: instancias concretas de cada dosis (son los elementos del min-heap E4).

| Columna | Tipo | Notas |
|---|---|---|
| `id` | `uuid` | PK |
| `paciente_id` | `uuid` | FK |
| `cronograma_id` | `uuid` | FK → `cronograma_dosis.id` |
| `programado_para` | `timestamptz` | **Prioridad del min-heap**, INDEX |
| `estado` | `enum('PENDIENTE','ENVIADO','POSPUESTO','CONFIRMADO','OMITIDO')` | |
| `enviado_en`, `confirmado_en` | `timestamptz` | |
| `veces_pospuesto` | `smallint` | default 0 |
| `inyeccion_id` | `uuid` | FK NULL: se llena al confirmar con registro (HU-16) |

**`suscripcion_push`**: dispositivos del usuario (R15). Tiene `id`, `usuario_id` (FK), `endpoint` (UNIQUE), `p256dh`, `auth`, `user_agent` y `creado_en`.

### Asistente IA (R28–R30)

**`mensaje_asistente`**

| Columna | Tipo | Notas |
|---|---|---|
| `id` | `uuid` | PK |
| `paciente_id` | `uuid` | FK |
| `rol` | `enum('USER','ASSISTANT','TOOL')` | |
| `contenido` | `text` | |
| `tool_nombre` | `varchar(40)` | NULL |
| `proveedor`, `modelo` | `varchar(40)` | p. ej. `deepseek`, `deepseek-chat` |
| `tokens_entrada`, `tokens_salida` | `int` | Control de costo |
| `bloqueado_por_guardrail` | `boolean` | R30 |
| `creado_en` | `timestamptz` | |

## Relaciones

- `usuario` 1–0..1 `paciente`; `usuario` 1–0..1 `medico`.
- `paciente` N–M `medico` a través de `vinculo_medico_paciente`.
- `paciente` 1–N `inyeccion`, `cronograma_dosis`, `recordatorio`, `mensaje_asistente` y `codigo_vinculo`.
- `cronograma_dosis` 1–N `recordatorio`; `recordatorio` 0..1–1 `inyeccion`.
- `zona_macro` 1–N `inyeccion`.
- `usuario` 1–N `refresh_token`, `reset_password_token` y `suscripcion_push`.

## De la BD a las estructuras de datos

| Tabla / consulta | Estructura en memoria | Cuándo |
|---|---|---|
| `paciente.tam_cuadricula` + `zona_macro` | 8 × **Matriz** (4 macros × 2 lados) | Al construir el `EstadoPaciente` |
| Última `inyeccion` por `microzona_id` | **Tabla hash** índice → `Microzona.ultimo_uso` | Al construir |
| `inyeccion` en los últimos 30 días agrupadas por macro | **Tabla hash** `uso_macro` | Al construir |
| `inyeccion` REGISTRADA de las últimas 24 h (orden asc.) | **Pila** de deshacer | Al construir |
| `inyeccion` ordenadas por `aplicada_en` | **Lista doblemente enlazada** del historial | Al construir o paginar |
| Matrices | **Grafo** de vecindad | Al construir |
| `recordatorio` PENDIENTE/POSPUESTO de las próximas 24 h | **Min-heap** indexado | Al iniciar el proceso y al guardar el cronograma |
| `EstadoPaciente` completo | **Caché LRU** | Primer acceso de cada paciente |

## Migraciones y datos semilla

- Alembic: `alembic revision --autogenerate`; cada PR con cambios de esquema incluye su migración.
- *Seed* inicial:
  - `zona_macro` con 4 filas.
  - `config_parametros` con los valores de ejemplo y `validado_clinicamente = false`.
  - Usuarios demo: `paciente@demo.insumap` y `medico@demo.insumap`, solo en local.

## Privacidad

Los datos de inyecciones son **datos de salud (sensibles)**. Ver [Requerimientos no funcionales](Requerimientos-no-funcionales.md): cifrado en tránsito, acceso por rol, consentimiento al registrarse y borrado de la cuenta.

Relacionadas: [API](API.md) · [Arquitectura](Arquitectura.md) · [Trazabilidad](Trazabilidad.md)
