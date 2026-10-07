# Módulo IA: Asistente del paciente (`Insumap-ai`)

## 1. Objetivo

Ayudar al paciente a **identificar y ubicar** sus zonas de aplicación usando lenguaje natural:

| Caso de uso | Ejemplo de pregunta | HU / Req. |
|---|---|---|
| ¿Dónde me inyecto ahora? | "¿Dónde me toca?" | HU-28 / R28 |
| Ubicar la zona en el cuerpo | "¿Dónde queda exactamente GLU-D-1-1?" → "Glúteo derecho, cuadrante superior externo: imagina una cruz sobre la nalga y usa la parte de arriba hacia afuera" | HU-28 / R28 |
| Explicar la sugerencia y los colores | "¿Por qué no el abdomen?" → "Usaste el abdomen 20 veces este mes, bastante más que las otras zonas…" | HU-29 / R29 |
| Resumen de su rotación | "¿Cómo voy esta semana?" | HU-29 / R29 |
| Rechazo seguro | "¿Cuántas unidades me pongo?" → se niega y lo remite al médico | HU-30 / R30 |

**El asistente no decide nada.** La sugerencia la calcula el algoritmo determinista del backend (max-heap, ver [Estructuras de datos y algoritmos](Estructuras-de-datos-y-algoritmos.md)). El LLM **solo la explica y la ubica**, y siempre con datos reales obtenidos por tools.

## 2. Arquitectura y flujo

![Secuencia del asistente](images/seq-asistente.png)

1. El frontend llama `POST /api/v1/asistente/mensajes` al **backend** (nunca a la IA directamente).
2. El backend valida el JWT, aplica el rate limit (20/h), guarda el mensaje y llama `POST {AI_SERVICE_URL}/chat` con:
   - `X-Service-Token`
   - un **token delegado** del paciente (JWT de 2 min con alcance `asistente:lectura`)
   - los últimos 10 mensajes
3. `Insumap-ai` aplica el **guardrail de entrada** y llama al LLM con el system prompt y la definición de las tools.
4. Cuando el LLM pide una tool, `Insumap-ai` ejecuta `GET` al backend con el token delegado y devuelve el resultado al LLM. Se permiten **máximo 4 rondas** de tools.
5. Se aplica el **guardrail de salida**, que verifica que los IDs de microzona mencionados existen y que no hay contenido de dosis.
6. Responde `{respuesta, microzonas_referidas, tokens, modelo}`. El backend lo guarda en `mensaje_asistente` y lo devuelve al frontend.

## 3. Proveedor LLM intercambiable

DeepSeek y Qwen exponen APIs **compatibles con OpenAI**. Por eso el código usa siempre el SDK `openai` y el proveedor se elige solo con variables de entorno:

```python
# Insumap-ai/app/llm/client.py
from openai import OpenAI
from app.config import settings

client = OpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)

def chat(messages, tools):
    return client.chat.completions.create(
        model=settings.LLM_MODEL, messages=messages, tools=tools,
        temperature=0.2, max_tokens=400,
    )
```

| Proveedor | `LLM_BASE_URL` | `LLM_MODEL` | Rol |
|---|---|---|---|
| **DeepSeek** | `https://api.deepseek.com` | `deepseek-chat` | Principal (el más barato, function calling) |
| **Qwen** (Alibaba Model Studio, internacional) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | `qwen-plus` (o `qwen-turbo`, más barato) | Respaldo |
| Otro compatible con OpenAI (por ejemplo, vía OpenRouter) | según el proveedor | según el proveedor | Opcional |

> Las URLs, nombres de modelo y precios deben **verificarse en la documentación oficial** al implementar, porque cambian con frecuencia.

**Respaldo automático:** si el proveedor principal responde 5xx o hay un *timeout* de 15 s, se reintenta una vez con el secundario (`LLM_FALLBACK_*`). Si también falla, el backend responde `degradado: true` con un texto de plantilla armado a partir de `/sugerencias`. El paciente siempre recibe la sugerencia.

## 4. Tools (function calling)

| Tool | Parámetros | Llama a | Devuelve |
|---|---|---|---|
| `get_sugerencia` | `k: int = 3` | `GET /sugerencias?k=` | Top-k con el desglose del score |
| `get_mapa` | `macro?: ABD\|MUS\|BRA\|GLU` | `GET /mapa` (filtrado) | Colores, ratio y horas restantes |
| `get_historial` | `dias: int = 7` | `GET /historial?desde=` | Aplicaciones recientes y conteo por macro |
| `describir_ubicacion` | `microzona_id: str` | **local** (sin backend) | Texto anatómico determinista: macro, lado y posición relativa en la cuadrícula ("tercio superior, hacia afuera") y las referencias de seguridad (p. ej., "a 5 cm del ombligo") |

```json
{ "type": "function", "function": {
  "name": "get_sugerencia",
  "description": "Obtiene las microzonas recomendadas para la próxima inyección, calculadas por el algoritmo de Insumap.",
  "parameters": { "type": "object", "properties": { "k": { "type": "integer", "minimum": 1, "maximum": 5 } } } } }
```

`describir_ubicacion` es **código determinista**, no generado por el LLM. Así, la ubicación anatómica siempre es la misma y se puede revisar.

## 5. System prompt (versionado en `prompts/system.md`)

```text
Eres el asistente de Insumap. Ayudas a pacientes con diabetes a UBICAR y ENTENDER
las zonas de inyección sugeridas por la app. Reglas:
1. Nunca inventes datos: usa siempre las herramientas para conocer el mapa, la
   sugerencia o el historial.
2. Para indicar dónde inyectarse usa get_sugerencia y luego describir_ubicacion.
3. NO das indicaciones sobre dosis, tipo de insulina, horarios de medicación,
   glucosa, ni diagnósticos. Si te lo piden, responde que eso lo define su médico
   tratante.
4. Si el usuario describe dolor intenso, bultos, enrojecimiento, hipoglucemia o una
   emergencia, recomienda contactar a su médico o a urgencias.
5. Responde en español, claro, en máximo 5 frases, con tono cálido.
6. Menciona el ID de microzona entre paréntesis, p. ej. (GLU-D-1-1).
```

## 6. Guardrails (R30)

| Capa | Regla | Acción |
|---|---|---|
| Entrada | Patrones de dosis o medicación ("unidades", "UI", "cuánta insulina", "dosis de") | Respuesta fija sin llamar al LLM (ahorra costo) |
| Entrada | Más de 500 caracteres o intento de *prompt injection* ("ignora tus instrucciones") | Se trunca o se rechaza |
| Salida | IDs de microzona que no existen en el mapa del paciente | Se elimina la mención y se registra en el log |
| Salida | Números seguidos de "unidades/UI" | Se reemplaza por el mensaje de remisión al médico |
| Global | Máximo 20 mensajes/hora, 400 tokens de salida y 4 rondas de tools | 429 o se corta |
| Datos | Al LLM solo se envían el nombre de pila y los datos del mapa: **nada de email ni identificadores personales** | Minimización |

## 7. Costo estimado

Por mensaje: unos 1 500 tokens de entrada (prompt + tools + resultados) y unos 200 de salida. Con 3 personas probando y una demo con unos 2 000 mensajes en total, el costo con DeepSeek/Qwen es **del orden de centavos de dólar**. Se controla con `tokens_entrada`/`tokens_salida` en `mensaje_asistente`.

## 8. Pruebas

- **Unitarias:** cada tool con el backend *mockeado* (respx); `describir_ubicacion` con todos los IDs de un mapa 6×6.
- **Guardrails:** 30 frases de prueba (dosis, emergencias, inyección de prompt) → respuesta esperada.
- **Contrato:** las tools validan las respuestas contra el `openapi.json` del backend.
- **Evaluación manual:** 20 preguntas reales con una rúbrica (correcto / usa tools / respeta las reglas), registradas en `Insumap-ai/eval/`.

Relacionadas: [Arquitectura](Arquitectura.md) · [API](API.md) · [Riesgos](Riesgos.md)
