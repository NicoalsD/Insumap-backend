# Historias de usuario: Insumap

Backlog completo de las 30 historias de usuario del proyecto Insumap (HU-01 a HU-19 del producto base; HU-20 a HU-30 de autenticación, rol médico y asistente IA), con su validación INVEST y sus criterios de aceptación en Gherkin (en español).

| ID | Título | Valor de negocio |
|---|---|---|
| HU-01 | Mapa corporal 2D | Identificar visualmente las zonas de aplicación. |
| HU-02 | Cuadrícula de microzonas | Precisar los puntos disponibles para rotación. |
| HU-03 | Registrar inyección | Registrar la aplicación desde el mapa. |
| HU-04 | Advertencia de zona no recuperada | Informar el riesgo sin impedir la decisión del paciente. |
| HU-05 | Deshacer último registro | Corregir un registro accidental. |
| HU-06 | Restaurar estado al deshacer | Mantener la información del mapa consistente. |
| HU-07 | Código de colores | Comprender el nivel de recuperación. |
| HU-08 | Bloqueo posterior a aplicación | Evitar recomendar inmediatamente el punto utilizado. |
| HU-09 | Almacenar hora de aplicación | Contar con la base temporal del cálculo. |
| HU-10 | Calcular recuperación biológica | Estimar cuándo vuelve a estar disponible cada microzona. |
| HU-11 | Sugerir punto óptimo | Elegir el punto con mayor recuperación. |
| HU-12 | Penalizar zonas sobreutilizadas | Favorecer una rotación equilibrada. |
| HU-13 | Priorizar zonas olvidadas | Recuperar puntos no utilizados durante largo tiempo. |
| HU-14 | Configurar cronograma | Adaptar recordatorios al tratamiento prescrito. |
| HU-15 | Enviar recordatorios | Reducir olvidos en las dosis. |
| HU-16 | Gestionar recordatorio | Permitir posponer o confirmar una dosis. |
| HU-17 | Guardar historial | Conservar trazabilidad de cada aplicación. |
| HU-18 | Consultar historial | Revisar aplicaciones anteriores. |
| HU-19 | Exportar historial | Compartir información útil con el médico. |
| HU-20 | Registrar cuenta | Crear un acceso personal y seguro como paciente o médico. |
| HU-21 | Iniciar sesión | Acceder a los datos propios de forma segura. |
| HU-22 | Mantener y cerrar sesión | No tener que iniciar sesión en cada uso y poder salir en dispositivos compartidos. |
| HU-23 | Recuperar contraseña | Recuperar el acceso sin perder el historial. |
| HU-24 | Vincular médico con código | Compartir información con el médico de forma controlada. |
| HU-25 | Médico consulta mapa del paciente | Ver la rotación del paciente sin depender de archivos. |
| HU-26 | Médico consulta y exporta historial | Revisar la adherencia antes o durante la consulta. |
| HU-27 | Revocar acceso del médico | Mantener el control del paciente sobre sus datos. |
| HU-28 | Preguntar al asistente dónde aplicar | Ubicar la zona sugerida en lenguaje natural. |
| HU-29 | Entender mi rotación con el asistente | Comprender colores, sugerencias y hábitos. |
| HU-30 | Respuestas seguras del asistente | Evitar consejos clínicos fuera del alcance de la app. |

---

## HU-01: Mapa corporal 2D

**Como** paciente dependiente de insulina
**Quiero** visualizar mi cuerpo dividido en abdomen, muslos, brazos y glúteos
**Para** identificar las zonas disponibles para aplicar mis inyecciones

**Validación INVEST**
- I — Independent: Puede entregarse como visualización base.
- N — Negotiable: Define el qué, no la solución técnica.
- V — Valuable: Facilita la rotación corporal.
- E — Estimable: Zonas macro claramente definidas.
- S — Small: Alcance limitado al mapa 2D.
- T — Testable: Se verifica la presencia de las cuatro zonas.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Visualización del mapa corporal 2D

  Escenario: Mostrar las zonas macro
    Dado que el paciente abre el mapa corporal
    Cuando el sistema carga la vista principal
    Entonces muestra un mapa corporal en 2D
    Y muestra las zonas abdomen, muslos, brazos y glúteos
```

**Supuestos / preguntas abiertas**
- La vista 2D será la primera versión; no se incluye una vista 3D.
- La representación gráfica y la orientación de cada zona quedan para diseño.

---

## HU-02: Cuadrícula de microzonas

**Como** paciente dependiente de insulina
**Quiero** ver cada zona macro subdividida en una cuadrícula configurable
**Para** seleccionar puntos concretos y rotar las aplicaciones

**Validación INVEST**
- I — Independent: Puede configurarse sobre el mapa existente.
- N — Negotiable: No impone una implementación visual.
- V — Valuable: Aumenta la precisión de la rotación.
- E — Estimable: Incluye tamaños definidos.
- S — Small: Se limita a configuración y representación.
- T — Testable: Se comprueba la cuadrícula seleccionada.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Subdivisión configurable de zonas corporales

  Esquema del escenario: Mostrar la cuadrícula seleccionada
    Dado que el paciente configura una cuadrícula de <tamaño>
    Cuando visualiza una zona macro
    Entonces el sistema divide la zona en una cuadrícula de <tamaño>

    Ejemplos:
      | tamaño |
      | 2x2    |
      | 4x4    |
      | 6x6    |
```

**Supuestos / preguntas abiertas**
- Se asumen 2×2, 4×4 y 6×6 como opciones iniciales.

---

## HU-03: Registrar inyección

**Como** paciente dependiente de insulina
**Quiero** registrar una inyección tocando una microzona del mapa
**Para** mantener actualizado mi tratamiento y la rotación de puntos

**Validación INVEST**
- I — Independent: Usa la microzona visible como unidad de registro.
- N — Negotiable: No fija detalles técnicos.
- V — Valuable: Evita depender de la memoria.
- E — Estimable: Acción y resultado están definidos.
- S — Small: Flujo principal de registro.
- T — Testable: Se verifica el registro de la microzona.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Registro de una inyección desde el mapa

  Escenario: Registrar una inyección en una microzona disponible
    Dado que el paciente visualiza una microzona disponible
    Cuando toca la microzona para registrar la aplicación
    Entonces el sistema registra la inyección
    Y asocia el registro con la microzona seleccionada
```

**Supuestos / preguntas abiertas**
- La fecha y hora se registran automáticamente según la hora del dispositivo o servidor.

---

## HU-04: Advertencia de zona no recuperada

**Como** paciente dependiente de insulina
**Quiero** recibir una advertencia antes de usar una microzona roja o amarilla
**Para** conocer el riesgo y decidir conscientemente si continúo

**Validación INVEST**
- I — Independent: Es una confirmación previa al registro.
- N — Negotiable: No impone diseño ni texto técnico.
- V — Valuable: Informa sin bloquear una necesidad clínica.
- E — Estimable: Colores y comportamiento están definidos.
- S — Small: Se limita al flujo alternativo.
- T — Testable: Se comprueban advertencia y continuación.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Advertencia al usar una microzona no recuperada

  Esquema del escenario: Advertir antes del registro
    Dado que la microzona seleccionada está en estado <estado>
    Cuando el paciente intenta registrar una inyección
    Entonces el sistema muestra una advertencia previa
    Y permite continuar o cancelar el registro

    Ejemplos:
      | estado   |
      | roja     |
      | amarilla |
```

**Supuestos / preguntas abiertas**
- El texto exacto de la advertencia y sus opciones queda para validación clínica y UX.

---

## HU-05: Deshacer último registro

**Como** paciente dependiente de insulina
**Quiero** deshacer el último registro de inyección
**Para** corregir una selección o registro accidental

**Validación INVEST**
- I — Independent: Se centra en la acción de deshacer.
- N — Negotiable: No impone control ni tecnología.
- V — Valuable: Permite corregir errores.
- E — Estimable: El registro afectado está identificado.
- S — Small: Flujo acotado.
- T — Testable: Se verifica la reversión del último evento.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Deshacer el último registro de inyección

  Escenario: Deshacer el último registro
    Dado que existe un registro de inyección como último evento
    Cuando el paciente selecciona deshacer
    Entonces el sistema deshace ese registro
    Y lo identifica con estado "deshecho"

  Escenario: No existe registro para deshacer
    Dado que no existe un registro de inyección pendiente de deshacer
    Cuando el paciente intenta deshacer
    Entonces el sistema no modifica ningún registro
```

**Supuestos / preguntas abiertas**
- Solo se puede deshacer hasta registrar la siguiente inyección.

---

## HU-06: Restaurar estado al deshacer

**Como** paciente dependiente de insulina
**Quiero** que una microzona recupere su estado anterior al deshacer
**Para** que el mapa refleje correctamente su disponibilidad

**Validación INVEST**
- I — Independent: Define el resultado de una reversión.
- N — Negotiable: No prescribe almacenamiento técnico.
- V — Valuable: Evita información incorrecta en el mapa.
- E — Estimable: Estado anterior y posterior son verificables.
- S — Small: Complementa el flujo de deshacer.
- T — Testable: Se compara el estado antes y después.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Restauración del estado de una microzona

  Escenario: Restaurar el estado anterior
    Dado que una microzona tenía un estado y disponibilidad previos al registro
    Y el registro es el último evento
    Cuando el paciente deshace el registro
    Entonces la microzona recupera su estado de color anterior
    Y recupera su disponibilidad anterior
```

**Supuestos / preguntas abiertas**
- El registro permanece en el historial con estado "deshecho", aunque el mapa se restaure.

---

## HU-07: Código de colores de recuperación

**Como** paciente dependiente de insulina
**Quiero** identificar el nivel de recuperación de cada microzona por colores
**Para** elegir un punto adecuado de aplicación

**Validación INVEST**
- I — Independent: Puede mostrarse con los estados calculados o configurados.
- N — Negotiable: No impone una tecnología de visualización.
- V — Valuable: Hace comprensible la disponibilidad.
- E — Estimable: Incluye exactamente tres estados.
- S — Small: Se limita a la representación.
- T — Testable: Se verifican rojo, amarillo y verde.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Representación visual de recuperación

  Escenario: Mostrar los tres estados de recuperación
    Dado que el mapa contiene microzonas con distintos niveles de recuperación
    Cuando el paciente visualiza el mapa
    Entonces cada microzona se representa en rojo, amarillo o verde
    Y cada color corresponde a un nivel de recuperación
```

**Supuestos / preguntas abiertas**
- Los rangos son configurables por el equipo médico: inicialmente rojo 0–24 h, amarillo 24–72 h y verde más de 72 h.

---

## HU-08: Bloqueo posterior a la aplicación

**Como** paciente dependiente de insulina
**Quiero** que la microzona utilizada pase automáticamente a rojo
**Para** evitar reutilizarla mientras el tejido se recupera

**Validación INVEST**
- I — Independent: Se activa al registrar una aplicación.
- N — Negotiable: No fija el mecanismo técnico.
- V — Valuable: Protege la rotación del punto utilizado.
- E — Estimable: Estado resultante definido.
- S — Small: Una regla posterior al registro.
- T — Testable: Se verifica el color rojo y bloqueo.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Bloqueo de la microzona utilizada

  Escenario: Marcar la microzona como roja
    Dado que el paciente registra una aplicación en una microzona
    Cuando el registro se confirma
    Entonces la microzona cambia automáticamente a estado rojo
    Y queda marcada como bloqueada
```

**Supuestos / preguntas abiertas**
- Deshacer revierte este cambio conforme a HU-06.

---

## HU-09: Almacenar hora de aplicación

**Como** paciente dependiente de insulina
**Quiero** que cada aplicación conserve su fecha y hora
**Para** calcular la recuperación y consultar mi tratamiento

**Validación INVEST**
- I — Independent: Se entrega con el registro de la aplicación.
- N — Negotiable: No impone formato interno.
- V — Valuable: Proporciona trazabilidad temporal.
- E — Estimable: El dato requerido está claro.
- S — Small: Una regla de persistencia del evento.
- T — Testable: Se verifica la fecha y hora guardadas.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Registro temporal de una aplicación

  Escenario: Guardar la hora del evento
    Dado que el paciente registra una aplicación
    Cuando el sistema confirma el registro
    Entonces almacena la fecha y hora del evento
    Y usa ese momento como referencia para la recuperación
```

**Supuestos / preguntas abiertas**
- La zona horaria aplicable será la del paciente; queda por definir el tratamiento de cambios de zona horaria.

---

## HU-10: Calcular recuperación biológica

**Como** paciente dependiente de insulina
**Quiero** conocer el tiempo estimado de recuperación de cada microzona
**Para** decidir dónde aplicar la siguiente dosis con menor riesgo de repetición

**Validación INVEST**
- I — Independent: Consume el historial temporal disponible.
- N — Negotiable: Expresa la regla de negocio, no su implementación.
- V — Valuable: Apoya una rotación informada.
- E — Estimable: Entradas principales identificadas.
- S — Small: Se limita al cálculo por microzona.
- T — Testable: Puede verificarse con datos de referencia médica.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Cálculo del tiempo de recuperación

  Escenario: Calcular la recuperación de una microzona utilizada
    Dado que una microzona tiene una zona corporal definida
    Y existe la fecha de su último uso y su historial de frecuencia
    Cuando el sistema calcula su recuperación
    Entonces considera la zona corporal, el tiempo transcurrido y la frecuencia histórica
    Y muestra el tiempo estimado según la regla médica configurada
```

**Supuestos / preguntas abiertas**
- El equipo médico proporcionará la fórmula o tabla de cálculo.
- Los rangos rojo, amarillo y verde también serán configurables por el equipo médico.

---

## HU-11: Sugerir punto óptimo

**Como** paciente dependiente de insulina
**Quiero** recibir una sugerencia automática de microzona
**Para** aplicar la siguiente dosis en el punto con mayor recuperación

**Validación INVEST**
- I — Independent: Puede consumir el cálculo de recuperación disponible.
- N — Negotiable: No fija el algoritmo técnico.
- V — Valuable: Reduce la carga de decidir y memorizar.
- E — Estimable: Regla de selección definida.
- S — Small: Se limita a mostrar la mejor opción.
- T — Testable: Se compara con los tiempos calculados.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Sugerencia de microzona óptima

  Escenario: Sugerir la microzona con mayor recuperación
    Dado que existen varias microzonas con tiempos de recuperación calculados
    Cuando el sistema genera la sugerencia para la siguiente dosis
    Entonces selecciona la microzona con mayor tiempo de recuperación
    Y la identifica como punto óptimo para la aplicación
```

**Supuestos / preguntas abiertas**
- Los empates y la combinación con penalizaciones o zonas olvidadas se resuelven según HU-12 y HU-13.

---

## HU-12: Penalizar zonas macro sobreutilizadas

**Como** paciente dependiente de insulina
**Quiero** que se penalicen las zonas macro usadas por encima del promedio
**Para** distribuir las aplicaciones de forma equilibrada

**Validación INVEST**
- I — Independent: Es una regla independiente de priorización.
- N — Negotiable: No impone el algoritmo de penalización.
- V — Valuable: Favorece la rotación entre zonas macro.
- E — Estimable: Periodo y condición están definidos.
- S — Small: Se limita a la comparación y penalización.
- T — Testable: Se verifica con conteos controlados.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Penalización de zonas macro sobreutilizadas

  Escenario: Penalizar una zona por encima del promedio
    Dado que se comparan los usos de las zonas macro durante 30 días
    Y una zona supera el promedio de uso de las demás
    Cuando el sistema calcula la sugerencia
    Entonces aplica la penalización configurada a esa zona macro
    Y reduce su prioridad frente a zonas no sobreutilizadas
```

**Supuestos / preguntas abiertas**
- El periodo predeterminado es 30 días y puede configurarse.
- El porcentaje o fórmula de penalización es configurable.

---

## HU-13: Priorizar zonas olvidadas

**Como** paciente dependiente de insulina
**Quiero** que se prioricen microzonas sin uso durante 15 días o más
**Para** recuperar la rotación de puntos que he dejado de utilizar

**Validación INVEST**
- I — Independent: Es una regla independiente de sugerencia.
- N — Negotiable: Define el objetivo, no la implementación.
- V — Valuable: Evita concentrar aplicaciones en pocos puntos.
- E — Estimable: Umbral y efecto están definidos.
- S — Small: Se limita a la bonificación de prioridad.
- T — Testable: Se verifica el umbral de 15 días.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Priorización de microzonas olvidadas

  Escenario: Bonificar una microzona sin uso reciente
    Dado que una microzona no se utiliza desde hace 15 días o más
    Cuando el sistema calcula la sugerencia
    Entonces aplica una bonificación de prioridad a esa microzona
    Y la considera junto con el tiempo de recuperación calculado
```

**Supuestos / preguntas abiertas**
- La bonificación puede ser superada por otra regla de seguridad o prioridad clínica.
- El valor de la bonificación queda para definición del equipo médico.

---

## HU-14: Configurar cronograma de dosis

**Como** paciente dependiente de insulina
**Quiero** configurar los horarios y la frecuencia diaria de mis dosis
**Para** recibir recordatorios acordes con mi tratamiento

**Validación INVEST**
- I — Independent: Puede configurarse como una funcionalidad propia.
- N — Negotiable: No impone almacenamiento ni plataforma.
- V — Valuable: Adapta la aplicación a la prescripción.
- E — Estimable: Frecuencia y horarios están definidos.
- S — Small: Flujo acotado de configuración.
- T — Testable: Se verifica la configuración guardada.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Configuración del cronograma de dosis

  Escenario: Guardar un cronograma diario
    Dado que el paciente configura una frecuencia de 1 a 6 dosis diarias
    Y asigna un horario a cada dosis
    Cuando guarda el cronograma
    Entonces el sistema conserva la frecuencia y los horarios configurados
    Y los utiliza como base para los recordatorios
```

**Supuestos / preguntas abiertas**
- Se permite una frecuencia de 1 a 6 dosis diarias.
- La validación clínica de horarios y dosis queda fuera de este requisito.

---

## HU-15: Enviar recordatorios de dosis

**Como** paciente dependiente de insulina
**Quiero** recibir una notificación para cada dosis programada
**Para** reducir el riesgo de olvidar una aplicación

**Validación INVEST**
- I — Independent: Usa un cronograma configurado.
- N — Negotiable: No impone proveedor de notificaciones.
- V — Valuable: Apoya la adherencia al tratamiento.
- E — Estimable: Evento y momento están definidos.
- S — Small: Se limita al envío de recordatorios.
- T — Testable: Se verifica la notificación en cada horario.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Recordatorios de dosis programadas

  Escenario: Enviar recordatorio en el horario configurado
    Dado que el paciente tiene un cronograma activo
    Y existe una dosis programada para el horario actual
    Cuando llega ese horario
    Entonces el sistema envía una notificación de recordatorio
    Y la notificación identifica la dosis pendiente
```

**Supuestos / preguntas abiertas**
- Se requiere permiso del sistema operativo para enviar notificaciones.
- La entrega puede depender de la configuración del dispositivo.

---

## HU-16: Gestionar un recordatorio

**Como** paciente dependiente de insulina
**Quiero** posponer o confirmar una notificación recibida
**Para** gestionar la dosis según mi situación inmediata

**Validación INVEST**
- I — Independent: Se centra en las acciones sobre un recordatorio.
- N — Negotiable: No impone interfaz ni mecanismo de posposición.
- V — Valuable: Da control al paciente sin perder el aviso.
- E — Estimable: Acciones permitidas están claras.
- S — Small: Flujo alternativo acotado.
- T — Testable: Se verifican posponer y confirmar.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Gestión de una notificación de recordatorio

  Escenario: Posponer un recordatorio
    Dado que el paciente recibe una notificación de dosis
    Cuando selecciona posponer y elige un tiempo
    Entonces el sistema programa un nuevo recordatorio para el tiempo elegido

  Escenario: Confirmar un recordatorio
    Dado que el paciente recibe una notificación de dosis
    Cuando selecciona confirmar
    Entonces el sistema marca el recordatorio como atendido
    Y pregunta si desea registrar la inyección
```

**Supuestos / preguntas abiertas**
- El tiempo de posposición lo elige el paciente.
- Confirmar no registra automáticamente la inyección.

---

## HU-17: Guardar historial de aplicaciones

**Como** paciente dependiente de insulina
**Quiero** conservar los datos de cada aplicación
**Para** tener trazabilidad de mi tratamiento y sus correcciones

**Validación INVEST**
- I — Independent: Se vincula al registro, pero es una capacidad diferenciable.
- N — Negotiable: No impone modelo de datos.
- V — Valuable: Conserva información clínica relevante.
- E — Estimable: Campos requeridos definidos.
- S — Small: Se limita al almacenamiento del historial.
- T — Testable: Se verifica cada campo del evento.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Historial de aplicaciones

  Escenario: Guardar una aplicación registrada
    Dado que el paciente registra una aplicación
    Cuando el sistema confirma el evento
    Entonces guarda fecha, hora, microzona y zona macro
    Y guarda el estado "registrado"

  Escenario: Actualizar el estado de una aplicación deshecha
    Dado que una aplicación registrada es el último evento
    Cuando el paciente la deshace
    Entonces el historial conserva el evento
    Y actualiza su estado a "deshecho"
```

**Supuestos / preguntas abiertas**
- Los estados válidos iniciales son "registrado" y "deshecho".

---

## HU-18: Consultar historial de aplicaciones

**Como** paciente dependiente de insulina
**Quiero** consultar dentro de la aplicación mis aplicaciones anteriores
**Para** revisar mi adherencia y la rotación de zonas

**Validación INVEST**
- I — Independent: Puede entregarse como consulta sobre el historial.
- N — Negotiable: No impone diseño de la consulta.
- V — Valuable: Permite seguimiento personal.
- E — Estimable: Datos consultables definidos por HU-17.
- S — Small: Se limita a visualizar registros.
- T — Testable: Se verifica la presencia de los eventos guardados.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Consulta del historial de aplicaciones

  Escenario: Consultar aplicaciones registradas
    Dado que el paciente tiene aplicaciones guardadas
    Cuando abre el historial dentro de la aplicación
    Entonces el sistema muestra sus aplicaciones
    Y muestra fecha, hora, microzona, zona macro y estado de cada una

  Escenario: Consultar un historial vacío
    Dado que el paciente no tiene aplicaciones guardadas
    Cuando abre el historial
    Entonces el sistema muestra que no existen aplicaciones registradas
```

**Supuestos / preguntas abiertas**
- El orden predeterminado será del evento más reciente al más antiguo; filtros quedan pendientes.

---

## HU-19: Exportar historial para el médico

**Como** paciente dependiente de insulina
**Quiero** exportar mi historial de aplicaciones
**Para** compartir información útil con mi médico tratante

**Validación INVEST**
- I — Independent: Puede consumir el historial sin alterar el registro.
- N — Negotiable: No impone una tecnología de exportación específica.
- V — Valuable: Facilita la revisión médica.
- E — Estimable: Formatos objetivo y contenido están definidos.
- S — Small: Se limita a generar y compartir el archivo.
- T — Testable: Se verifica el formato y la información.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Exportación del historial de aplicaciones

  Escenario: Exportar el historial en formatos disponibles
    Dado que el paciente tiene aplicaciones en su historial
    Cuando solicita exportarlo y selecciona PDF o CSV/Excel
    Entonces el sistema genera un archivo en el formato seleccionado
    Y el archivo incluye fecha, hora, microzona, zona macro y estado

  Escenario: Exportar un historial vacío
    Dado que el paciente no tiene aplicaciones registradas
    Cuando solicita exportar el historial
    Entonces el sistema informa que no hay datos para exportar
```

**Supuestos / preguntas abiertas**
- Se habilitan PDF y CSV/Excel.
- Queda por definir si se permite filtrar por fechas o zonas antes de exportar.

---

## HU-20: Registrar cuenta

**Como** usuario nuevo (paciente o médico)
**Quiero** crear una cuenta con mi email y una contraseña indicando mi rol
**Para** acceder a Insumap con mis datos protegidos

**Validación INVEST**
- I — Independent: No depende de otras HU.
- N — Negotiable: El formulario puede ajustarse.
- V — Valuable: Sin cuenta no hay datos personales.
- E — Estimable: Formulario y validaciones definidos.
- S — Small: Solo el alta de cuenta.
- T — Testable: Se verifica la creación y los errores.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Registro de cuenta

  Escenario: Registro exitoso de un paciente
    Dado que el usuario está en la pantalla de registro
    Cuando ingresa nombre, email válido, una contraseña de al menos 8 caracteres con un número
    Y selecciona el rol "Paciente" y acepta el tratamiento de datos de salud
    Entonces el sistema crea la cuenta
    Y lo dirige al mapa corporal con la sesión iniciada

  Escenario: Email ya registrado
    Dado que existe una cuenta con el email "ana@correo.com"
    Cuando un usuario intenta registrarse con "ana@correo.com"
    Entonces el sistema muestra "Este email ya está registrado"

  Escenario: Registro sin aceptar el tratamiento de datos
    Dado que el usuario completó el formulario
    Cuando no acepta el tratamiento de datos de salud
    Entonces el sistema no permite crear la cuenta
```

**Supuestos / preguntas abiertas**
- El médico registra además su número de registro profesional; no se verifica contra una entidad externa en esta versión.
- No se incluye inicio de sesión con Google en esta versión.

---

## HU-21: Iniciar sesión

**Como** usuario registrado
**Quiero** iniciar sesión con mi email y contraseña
**Para** acceder a mis datos desde cualquier dispositivo

**Validación INVEST**
- I — Independent: Requiere solo una cuenta existente.
- N — Negotiable: El diseño de la pantalla es flexible.
- V — Valuable: Protege los datos de salud.
- E — Estimable: Flujo estándar.
- S — Small: Solo la autenticación.
- T — Testable: Se verifican los casos válidos, inválidos y el bloqueo.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Inicio de sesión

  Escenario: Credenciales válidas de un paciente
    Dado que el paciente tiene una cuenta activa
    Cuando ingresa su email y contraseña correctos
    Entonces el sistema inicia la sesión
    Y muestra el mapa corporal

  Escenario: Credenciales válidas de un médico
    Dado que el médico tiene una cuenta activa
    Cuando inicia sesión correctamente
    Entonces el sistema muestra su lista de pacientes

  Escenario: Credenciales inválidas
    Cuando el usuario ingresa una contraseña incorrecta
    Entonces el sistema muestra "Email o contraseña incorrectos"
    Y no indica cuál de los dos datos falló

  Escenario: Demasiados intentos
    Dado que el usuario falló 5 intentos en 15 minutos
    Cuando intenta nuevamente
    Entonces el sistema le pide esperar antes de reintentar
```

**Supuestos / preguntas abiertas**
- El bloqueo es temporal (15 minutos) y por combinación de email e IP.

---

## HU-22: Mantener y cerrar sesión

**Como** usuario autenticado
**Quiero** que mi sesión se mantenga al volver a abrir la app y poder cerrarla
**Para** usar la app rápido sin comprometer mi seguridad

**Validación INVEST**
- I — Independent: Se apoya en HU-21.
- N — Negotiable: La duración es configurable.
- V — Valuable: Reduce la fricción diaria.
- E — Estimable: Tokens de acceso y renovación definidos.
- S — Small: Solo renovación y cierre.
- T — Testable: Se verifican la expiración y el cierre.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Sesión persistente y cierre de sesión

  Escenario: Volver a abrir la app con sesión vigente
    Dado que el usuario inició sesión hace menos de 7 días
    Cuando abre la aplicación
    Entonces el sistema lo dirige a su pantalla principal sin pedir credenciales

  Escenario: Sesión vencida
    Dado que pasaron más de 7 días sin usar la aplicación
    Cuando el usuario la abre
    Entonces el sistema muestra la pantalla de inicio de sesión

  Escenario: Cerrar sesión
    Dado que el usuario tiene una sesión activa
    Cuando selecciona "Cerrar sesión"
    Entonces el sistema invalida la sesión en ese dispositivo
    Y muestra la pantalla de inicio de sesión
```

**Supuestos / preguntas abiertas**
- Token de acceso de 15 minutos y de renovación de 7 días (configurables).

---

## HU-23: Recuperar contraseña

**Como** usuario que olvidó su contraseña
**Quiero** restablecerla mediante un enlace a mi email
**Para** recuperar el acceso sin perder mi historial

**Validación INVEST**
- I — Independent: Independiente del resto del flujo.
- N — Negotiable: El canal (email) puede cambiar.
- V — Valuable: Evita perder la cuenta.
- E — Estimable: Flujo de token definido.
- S — Small: Solicitud y restablecimiento.
- T — Testable: Se verifican la vigencia y el uso único.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Recuperación de contraseña

  Escenario: Solicitar recuperación
    Dado que el usuario está en "¿Olvidaste tu contraseña?"
    Cuando ingresa su email
    Entonces el sistema muestra "Si el email existe, enviamos un enlace"

  Escenario: Restablecer con enlace vigente
    Dado que el usuario recibió un enlace hace menos de 30 minutos
    Cuando define una nueva contraseña válida
    Entonces el sistema actualiza la contraseña
    Y cierra todas sus sesiones abiertas

  Escenario: Enlace vencido o ya usado
    Cuando el usuario abre un enlace vencido o usado
    Entonces el sistema indica que debe solicitar uno nuevo
```

**Supuestos / preguntas abiertas**
- El mensaje de solicitud es el mismo exista o no el email, para no revelar cuentas.

---

## HU-24: Vincular médico con código

**Como** paciente dependiente de insulina
**Quiero** generar un código temporal para que mi médico se vincule a mi cuenta
**Para** que mi médico pueda revisar mi rotación sin compartir mi contraseña

**Validación INVEST**
- I — Independent: Requiere cuentas de ambos roles.
- N — Negotiable: El formato del código es negociable.
- V — Valuable: Habilita el seguimiento médico.
- E — Estimable: Generación y canje definidos.
- S — Small: Solo el vínculo.
- T — Testable: Se verifican la vigencia y el uso único del código.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Vínculo médico-paciente

  Escenario: Paciente genera un código
    Dado que el paciente está en su perfil
    Cuando selecciona "Compartir con mi médico"
    Entonces el sistema muestra un código de 8 caracteres válido por 48 horas

  Escenario: Médico canjea un código válido
    Dado que el médico tiene el código vigente de un paciente
    Cuando lo ingresa en "Agregar paciente"
    Entonces el paciente aparece en su lista de pacientes

  Escenario: Código vencido o usado
    Cuando el médico ingresa un código vencido o ya usado
    Entonces el sistema indica que el código no es válido
```

**Supuestos / preguntas abiertas**
- Un paciente puede tener varios médicos vinculados.

---

## HU-25: Médico consulta mapa del paciente

**Como** médico tratante
**Quiero** ver el mapa corporal y los colores de recuperación de mi paciente
**Para** evaluar si está rotando correctamente sus zonas

**Validación INVEST**
- I — Independent: Reutiliza el mapa de HU-01/HU-07.
- N — Negotiable: La presentación puede variar.
- V — Valuable: Apoya la decisión clínica.
- E — Estimable: Vista de solo lectura.
- S — Small: Solo la consulta.
- T — Testable: Se verifican el acceso y la restricción.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Consulta del mapa por el médico

  Escenario: Médico vinculado consulta el mapa
    Dado que el médico está vinculado con el paciente
    Cuando abre el detalle del paciente
    Entonces el sistema muestra el mapa corporal con los colores actuales
    Y no permite registrar ni deshacer inyecciones

  Escenario: Médico no vinculado
    Dado que el médico no está vinculado con un paciente
    Cuando intenta consultar su mapa
    Entonces el sistema deniega el acceso
```

**Supuestos / preguntas abiertas**
- La vista del médico se optimiza para pantallas anchas, pero funciona en móvil.

---

## HU-26: Médico consulta y exporta historial

**Como** médico tratante
**Quiero** consultar y exportar el historial de aplicaciones de mi paciente
**Para** revisar su adherencia y su rotación en la consulta

**Validación INVEST**
- I — Independent: Reutiliza HU-17 a HU-19.
- N — Negotiable: Los filtros son negociables.
- V — Valuable: Facilita la consulta médica.
- E — Estimable: Formatos ya definidos en HU-19.
- S — Small: Consulta y exportación.
- T — Testable: Se verifican el contenido y el acceso.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Historial del paciente para el médico

  Escenario: Consultar historial del paciente
    Dado que el médico está vinculado con el paciente
    Cuando abre la pestaña Historial del paciente
    Entonces el sistema muestra las aplicaciones de la más reciente a la más antigua

  Escenario: Exportar historial del paciente
    Dado que el paciente tiene aplicaciones registradas
    Cuando el médico selecciona exportar en PDF
    Entonces el sistema genera el archivo con fecha, hora, microzona, zona macro y estado
```

**Supuestos / preguntas abiertas**
- El médico no puede modificar ningún registro.

---

## HU-27: Revocar acceso del médico

**Como** paciente dependiente de insulina
**Quiero** revocar el acceso de un médico vinculado
**Para** mantener el control sobre quién ve mis datos de salud

**Validación INVEST**
- I — Independent: Depende de HU-24.
- N — Negotiable: La ubicación de la opción es flexible.
- V — Valuable: Protege la privacidad.
- E — Estimable: Acción simple.
- S — Small: Solo la revocación.
- T — Testable: Se verifica la pérdida de acceso.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Revocación del vínculo

  Escenario: Revocar a un médico
    Dado que el paciente tiene un médico vinculado
    Cuando selecciona "Revocar" y confirma
    Entonces el médico deja de ver al paciente en su lista
    Y cualquier consulta posterior del médico a ese paciente es denegada
```

**Supuestos / preguntas abiertas**
- La revocación es inmediata y queda registrada con su fecha.

---

## HU-28: Preguntar al asistente dónde aplicar

**Como** paciente dependiente de insulina
**Quiero** preguntarle a un asistente en lenguaje natural dónde aplicarme la próxima dosis
**Para** ubicar fácilmente la zona sugerida en mi cuerpo

**Validación INVEST**
- I — Independent: Consume la sugerencia de HU-11.
- N — Negotiable: El tono y el formato son negociables.
- V — Valuable: Reduce la carga de decidir y ubicar.
- E — Estimable: Herramientas y flujo definidos.
- S — Small: Una pregunta y su respuesta.
- T — Testable: Se verifica la coherencia con la sugerencia del sistema.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Asistente para ubicar la zona

  Escenario: Preguntar dónde aplicar
    Dado que el paciente tiene microzonas registradas en su mapa
    Cuando pregunta al asistente "¿Dónde me inyecto ahora?"
    Entonces el asistente responde con la microzona sugerida por el sistema
    Y describe su ubicación en el cuerpo en lenguaje sencillo
    Y ofrece abrir esa microzona en el mapa

  Escenario: Servicio de IA no disponible
    Dado que el proveedor de IA no responde
    Cuando el paciente hace una pregunta
    Entonces el sistema muestra la sugerencia calculada sin explicación adicional
    Y avisa que el asistente no está disponible temporalmente
```

**Supuestos / preguntas abiertas**
- La sugerencia siempre la calcula el algoritmo; el asistente solo la explica.
- Proveedor: DeepSeek (principal) o Qwen (respaldo).

---

## HU-29: Entender mi rotación con el asistente

**Como** paciente dependiente de insulina
**Quiero** que el asistente me explique por qué se sugiere una zona, qué significan los colores y cómo va mi rotación
**Para** entender y mejorar mis hábitos de aplicación

**Validación INVEST**
- I — Independent: Usa datos ya disponibles.
- N — Negotiable: El nivel de detalle es negociable.
- V — Valuable: Mejora la comprensión y la adherencia.
- E — Estimable: Herramientas definidas.
- S — Small: Explicaciones basadas en datos.
- T — Testable: Se verifica que use datos reales.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Explicaciones del asistente

  Escenario: Explicar una sugerencia
    Dado que el sistema sugirió una microzona del glúteo
    Cuando el paciente pregunta "¿Por qué no el abdomen?"
    Entonces el asistente explica la razón usando el uso de cada zona en los últimos 30 días

  Escenario: Resumen semanal
    Cuando el paciente pregunta "¿Cómo voy esta semana?"
    Entonces el asistente resume cuántas aplicaciones hizo por zona macro en los últimos 7 días
```

**Supuestos / preguntas abiertas**
- El asistente nunca inventa datos: todo proviene de las herramientas.

---

## HU-30: Respuestas seguras del asistente

**Como** paciente dependiente de insulina
**Quiero** que el asistente no me dé indicaciones de dosis ni diagnósticos y me remita a mi médico
**Para** no tomar decisiones clínicas peligrosas basadas en la app

**Validación INVEST**
- I — Independent: Transversal al asistente.
- N — Negotiable: Las frases exactas son negociables.
- V — Valuable: Protege al paciente.
- E — Estimable: Reglas definidas.
- S — Small: Solo los límites del asistente.
- T — Testable: Se verifica con frases de prueba.

**Criterios de aceptación (Gherkin)**
```gherkin
# language: es
Característica: Límites del asistente

  Escenario: Pregunta sobre dosis
    Cuando el paciente pregunta "¿Cuántas unidades me pongo hoy?"
    Entonces el asistente indica que la dosis la define su médico tratante
    Y no menciona ninguna cantidad

  Escenario: Señal de alarma
    Cuando el paciente menciona un bulto doloroso o una hipoglucemia
    Entonces el asistente recomienda contactar a su médico o a urgencias
```

**Supuestos / preguntas abiertas**
- Los mensajes bloqueados quedan marcados para revisión del equipo.
