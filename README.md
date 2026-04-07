# 🎭 PROMPT DE REFACCIÓN INTEGRAL: TUTOR INTELIGENTE MULTI-AGENTE (VERSION CONSOLA DIRECTA)

Vamos a implementar la lógica real del sistema. Este prompt integra la arquitectura de **Enrutador (Router)**, las capacidades de **Solución/Debugging** y la optimización para el **Clúster Nvidia A40 (48GB VRAM)**. 

**NOTA IMPORTANTE:** Se ha decidido POSPONER la implementación del "Senado" (Jurado/Validación). El flujo será lineal tras la toma de decisión del enrutador.

## 1. REDISEÑO DEL FLUJO (GRAFO CON ENRUTADOR)
Refactoriza `src/agents/state.py` y `graph.py` para implementar un flujo basado en intenciones:

- **State:** En `TutorState` añade: `tarea` ("generar", "resolver", "debug"), `con_solucion` (bool), `codigo_entrada` (str) y `resultado_codigo` (str).
- **Entry Point (Router):** El grafo comienza en un `router_node` que bifurca:
    - `generar_ejercicio` ➔ `retriever_node` ➔ `generate_exercise_node`.
    - `resolver_codigo` ➔ `solve_node`.
    - `buscar_bugs` ➔ `find_bugs_node`.
- **Lógica de Solución:** Tras `generate_exercise_node`, si `state["con_solucion"]` es True, pasa a `generate_solution_node`. Si es False, el flujo termina.

## 2. INTEGRACIÓN REAL DE LLM (ADIÓS MOCKS)
Refactoriza `src/agents/nodes.py` eliminando cualquier respuesta prefijada:
- **Modelo:** Usa `ChatOllama` de `langchain_ollama`.
- **Optimización Clúster:** Configura los nodos para que, si el entorno es `cluster`, aprovechen la potencia de la Nvidia A40 (puedes aumentar la complejidad de los System Prompts).
- **Nuevos Nodos:** Implementa la lógica real para `solve_node` (explicar y resolver código) y `find_bugs_node` (identificar errores).

## 3. CONFIGURACIÓN DUAL Y ENTORNO (.env)
Implementa un sistema que lea un archivo `.env`:
- `ENVIRONMENT`: (`local` | `cluster`).
- `OLLAMA_MODEL`: Dinámico (ej. `llama3.1:8b` o `llama3.1:70b`).
- `NUM_CTX`: 16384 (aprovechar VRAM de la A40).
- Organiza los archivos fuente (PDFs, conceptos) en la carpeta `/data`.

## 4. INTERFAZ DE CONSOLA INTERACTIVA (main.py)
Implementa un bucle principal interactivo:
1. **Generar Ejercicio:** Pide al usuario conceptos a practicar, dificultad y toggle de solución. Carga los "conceptos vistos" desde Neo4j para el filtro anti-frustración.
2. **Resolver Código:** Input multilínea para código del usuario.
3. **Buscar Bugs:** Input para analizar errores en código del usuario.
- **UX:** Imprime estados claros ("🔍 Buscando en el Grafo de Conocimiento...", "✍️ El LLM está redactando...").
- **Salida:** Formato Markdown legible en terminal para los enunciados y soluciones.

## 5. REQUISITOS TÉCNICOS
- Actualiza `requirements.txt` (langchain-ollama, pydantic, python-dotenv).
- **Filtro Anti-Frustración (CRÍTICO):** Asegura que la consulta Cypher en el retriever siga filtrando ejercicios para que NO contengan conceptos que el alumno no haya marcado como "vistos" en su historial.

**Procede con la implementación empezando por el State y el Grafo, terminando con la consola en main.py.**