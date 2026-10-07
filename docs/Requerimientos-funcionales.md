| ID | Requisito / regla |
| :--- | :--- |
| **R01** | El sistema debe mapear visualmente el cuerpo del paciente en 2D (3D como mejora futura), dividido en 4 zonas macro: abdomen, muslos, brazos y glúteos. |
| **R02** | El sistema debe subdividir cada zona macro en micro zonas de aplicación, mediante una cuadrícula de tamaño configurable. |
| **R03** | El paciente debe poder registrar una inyección tocando directamente la micro zona correspondiente en el mapa visual. |
| **R04** | El sistema debe permitir el registro de una inyección en una micro zona no recuperada (roja o amarilla), mostrando una advertencia previa sin bloquear la acción del usuario. |
| **R05** | El sistema debe permitir deshacer el último registro de inyección. |
| **R06** | Al deshacer un registro, el sistema debe restablecer el estado de color y disponibilidad que tenía la micro zona antes del registro. |
| **R07** | El sistema debe representar el nivel de recuperación de cada micro zona mediante un código de tres colores: rojo, amarillo y verde. |
| **R08** | Al registrar una aplicación, el sistema debe marcar automáticamente la micro zona utilizada con estado "rojo" (bloqueada). |
| **R09** | Al registrar una aplicación, el sistema debe almacenar el tiempo del evento como base para el cálculo de recuperación. |
| **R10** | El sistema debe calcular el tiempo estimado de recuperación biológica de cada micro zona, en función de la zona corporal, el tiempo transcurrido desde su último uso y su historial de frecuencia de uso. |
| **R11** | El sistema debe sugerir automáticamente la micro zona con mayor tiempo de recuperación como punto óptimo para la siguiente dosis. |
| **R12** | El sistema debe penalizar en el cálculo de sugerencia a las zonas macro cuyo uso acumulado supere el promedio de las demás zonas en un periodo de 30 días (configurable). |
| **R13** | El sistema debe priorizar en el cálculo de sugerencia las micro zonas sin uso durante 15 días o más ("zonas olvidadas"). |
| **R14** | El sistema debe permitir configurar un cronograma de dosis (horarios y frecuencia diaria). |
| **R15** | El sistema debe enviar notificaciones al paciente para recordar la aplicación de cada dosis, según el cronograma configurado. |
| **R16** | El sistema debe permitir al paciente posponer o confirmar una notificación de recordatorio recibida. |
| **R17** | El sistema debe almacenar un historial de cada aplicación registrada, incluyendo fecha, hora, micro zona, zona macro y estado (registrado/deshecho). |
| **R18** | El sistema debe permitir al paciente consultar su historial de aplicaciones dentro de la app. |
| **R19** | El sistema debe permitir exportar el historial de aplicaciones para el médico tratante. |
| **R20** | El sistema debe permitir el registro de usuarios con email, contraseña y rol (paciente o médico), previa aceptación del tratamiento de datos de salud. |
| **R21** | El sistema debe autenticar a los usuarios mediante email y contraseña y limitar los intentos fallidos. |
| **R22** | El sistema debe mantener la sesión del usuario mediante tokens renovables y permitir cerrarla. |
| **R23** | El sistema debe permitir recuperar la contraseña mediante un enlace temporal enviado al email. |
| **R24** | El sistema debe permitir al paciente generar un código temporal de un solo uso para vincular a un médico. |
| **R25** | El sistema debe permitir al médico vinculado consultar, en solo lectura, el mapa corporal de su paciente. |
| **R26** | El sistema debe permitir al médico vinculado consultar y exportar el historial de aplicaciones de su paciente. |
| **R27** | El sistema debe permitir al paciente revocar en cualquier momento el acceso de un médico vinculado. |
| **R28** | El sistema debe ofrecer un asistente conversacional que indique y describa en lenguaje natural la microzona sugerida por el algoritmo. |
| **R29** | El asistente debe explicar las sugerencias, los colores y el estado de rotación usando exclusivamente datos reales del paciente. |
| **R30** | El asistente no debe dar indicaciones de dosis, medicación ni diagnósticos, y debe remitir al médico tratante. |

> **Fuente de los IDs:** cada **R*nn*** corresponde 1 a 1 con la historia **HU-*nn***. Los requerimientos no funcionales están en [Requerimientos no funcionales](Requerimientos-no-funcionales.md) y la relación con el diseño en [Trazabilidad](Trazabilidad.md).
