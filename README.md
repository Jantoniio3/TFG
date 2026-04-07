# 🎭 PROMPT DE REFACCIÓN INTEGRAL: TUTOR INTELIGENTE MULTI-AGENTE (VERSION CONSOLA)

Hemos validado el esqueleto. Vamos a implementar la lógica real del sistema. Este prompt integra la nueva arquitectura de **Enrutador (Router)**, las capacidades de **Solución/Debugging** y la optimización para el **Clúster Nvidia A40 (48GB VRAM)**, manteniendo una interfaz de **Consola Interactiva**.

## 1. REDISEÑO DEL FLUJO (GRAFO CON ENRUTADOR)
Refactoriza `src/agents/state.py` y `graph.py` para implementar un flujo basado en intenciones:

- **State:** Añade en `TutorState` los campos: `tarea` ("generar", "resolver", "debug"), `con_solucion` (bool), `codigo_entrada` (str) y `resultado_codigo` (str).
- **Entry Point (Router):** El primer nodo debe ser un `router_node` que bifurque según `state["tarea"]`:
    - `generar_ejercicio` ➔ `retriever_node` (Graph RAG Neo4j).
    - `resolver_codigo` ➔ `solve_node`.
    - `buscar_bugs` ➔ `find_bugs_node`.
- **Salida Condicional:** En la generación, si `con_solucion` es False, el flujo termina tras el Jurado (Senado) sin pasar por el nodo de escritura de solución.

## 2. INTEGRACIÓN REAL DE LLM (ADIÓS MOCKS)
Refactoriza `src/agents/nodes.py` eliminando cualquier respuesta prefijada:
- **Modelo:** Usa `ChatOllama` de `langchain_ollama`.
- **El Jurado (Senado):** El nodo de validación debe usar `.with_structured_output()` con Pydantic para devolver un booleano `valido` y un `razonamiento`. 
- **Paralelismo (Cluster Ready):** Si la configuración indica entorno `cluster`, ejecuta los 3 agentes del Jurado de forma **asíncrona** (`asyncio.gather`) aprovechando la GPU A40.
- **Nuevos Nodos:** Implementa la lógica real para `solve_node` (explicar y resolver código) y `find_bugs_node` (identificar errores lógicos/sintácticos).

## 3. CONFIGURACIÓN DUAL Y ENTORNO (.env)
Implementa un sistema de configuración que lea un archivo `.env`:
- `ENVIRONMENT`: (`local` para modelos 8B | `cluster` para modelos 70B y A40).
- `ASYNC_JURY`: `True` si estamos en el clúster.
- `OLLAMA_MODEL`: Dinámico según el hardware (ej. llama3.1:8b o llama3.1:70b).
- `NUM_CTX`: 16384 (para aprovechar la VRAM en el clúster).
- Mueve toda la documentación y archivos fuente (PDFs, listas de conceptos) a la carpeta `/data`.

## 4. INTERFAZ DE CONSOLA INTERACTIVA (main.py)
Implementa un bucle principal en `main.py` que permita al usuario elegir la tarea:
1. **Generar Ejercicio:** Solicitar conceptos a practicar, dificultad y si desea ver la solución. El historial de "conceptos vistos" debe cargarse desde Neo4j.
2. **Resolver Código:** Solicitar al usuario que pegue su código (input multilínea).
3. **Buscar Bugs:** Solicitar código para analizar errores.
- **UX:** Imprime mensajes claros durante el proceso (ej: "🔍 Consultando Grafo...", "⚖️ El Jurado está deliberando (Intento X)...").
- **Salida:** Usa formato Markdown legible en consola para el enunciado y la solución.

## 5. REQUISITOS TÉCNICOS
- Actualiza `requirements.txt` (langchain-ollama, pydantic, python-dotenv).
- Asegura que el **Filtro Anti-Frustración** (Cypher) siga activo en el nodo retriever para no incluir conceptos no vistos por el alumno.

**Procede con la implementación empezando por el State y el Grafo, y termina con la lógica de la consola en main.py.**# TFG
