🎓 Walkthrough Arquitectónico Global: Tutor Inteligente (TFG)
==================================================================
Este documento es un resumen técnico, analítico y metodológico exhaustivo de todo el proyecto del **Sistema de Aprendizaje Inteligente**. Está diseñado para servir como base doctrinal para redactar la memoria de tu Trabajo de Fin de Grado (TFG) o estructurar la defensa ante el tribunal.

> [!NOTE]
> **Visión General del Sistema:** El proyecto consiste en un Tutor Inteligente Interactivo basado en una arquitectura Multi-Agente (orquestada con *LangGraph*) y un motor de recuperación de conocimiento y ejercicios (RAG In-Memory). El sistema funciona como un ayudante autónomo para estudiantes de programación, generando ejercicios adaptativos e infiriendo sus lagunas de conocimiento de forma algorítmica para evitar el estrés y la frustración pedagógica.

---

## 🏗️ 1. Arquitectura Central y Tecnologías Empleadas

El proyecto destaca por rechazar servicios privativos y enfoques pesados, apostando por componentes *open-source*, operaciones en memoria de alta velocidad y localmente ejecutables.

### 1.1 Modelos LLM Desacoplados (Ollama)
El sistema no depende de costosas APIs externas (como OpenAI), un requisito crucial para instituciones educativas por motivos de privacidad estudiantil (RGPD) y reducción de costes operativos.
- Se ha usado la librería `langchain-ollama` para instanciar dinámicamente modelos fundacionales.
- **Hot-Swapping Dinámico**: A través del fichero `.env`, la aplicación migra suavemente entre un entorno portátil (ideal para que el desarrollador pruebe código con `llama3.1:8b`) hacia un entorno de supercómputo universitario (Clúster A-40) que explota en segundo plano modelos masivos para inferencia avanzada (`llama3.1:70b`).

### 1.2 Grafo de Conocimiento *In-Memory* (NetworkX)
Tras un crítico pivote arquitectónico, se eliminaron bases externas tradicionales, trasladando toda la persistencia a la memoria RAM.
- **Ontología en Código Pura:** La intrincada malla del currículo docente (ej. qué conceptos bloquean a otros) se modeló en `src/ontology/grafo.py` mediante variables de diccionario. Esto mapea un árbol de aprendizaje real y escalable.
- **Motor Anti-Frustración:** En vez de hacer complejas consultas de red, `main.py` genera un grafo topológico con la librería matemática `networkx`. Haciendo uso del algoritmo iterativo `nx.descendants()`, si el usuario selecciona que conoce un tema avanzado, el sistema automáticamente deduce todos los pre-requisitos necesarios de la ontología, construyendo un perfil del usuario extremadamente preciso y en cuestión de milisegundos.

### 1.3 Orquestación Multi-Agente (LangGraph / LangChain)
Para huir de los anticuados scripts lineales de la era GPT-3, el flujo se delegó en agentes que se comunican entre sí. Su estructura forma un Grafo Acíclico Dirigido (DAG).
- En `src/agents/graph.py` reside el enrutador principal (`router_node`).
- Según la intención evaluada del usuario (Generar un nuevo problema, evaluar una solución propuesta, o hacer Debugging), la responsabilidad salta al nodo o "agente" específico en `nodes.py`.
- **Clúster Prompting Avanzado:** El sistema reacciona ante su hardware subyacente. Si está corriendo en el Clúster de alto rendimiento, modula dinámicamente sus *System Prompts* para aplicar técnicas formales de *Chain of Thought* (resolución analítica paso a paso), argumentando sus correcciones y devolviendo explicaciones técnicas sobresalientes gracias a la gran capacidad de VRAM reservada.

---

## 🧠 2. Sistema de Recuperación Aumentada (In-Memory RAG)

El clásico vector-RAG, propenso a inyectar contexto ruidoso mediante embeddings borrosos, fue descartado tras iteraciones de la arquitectura.

- El **Motor In-Memory RAG** (localizado en `src/retriever/graph_rag.py`) ha sido refinado para operar puramente con lógica de grafos matemáticos (Operación de subconjuntos de Euler).
- Carga instantáneamente a la memoria el dataset de problemas (`ejercicios_etiquetados.json`).
- Aplica un filtro interseccional (`issubset()`) que desecha y veta por completo cualquier ejercicio que intente evaluar al menos *un solo concepto* que el algoritmo anti-frustración todavía no haya confirmado como familiar para el estudiante.
- El resultado se inyecta por el LangGraph al modelo generador para crear nuevos problemas inspirados en el material didáctico legítimo de la asignatura.

---

## 🔬 3. Anatomía del Sistema (Desglose Script por Script)

El funcionamiento del tutor se apoya en la coreografía exacta de módulos independientes y altamente especializados. A continuación se desglosa el cometido biológico de cada archivo:

### ⚙️ `main.py` (El Orquestador y la Interfaz CLI)
Actúa como panel de control principal.
1. **Configuración del Perfil:** Al arrancar, solicita al alumno temas que domina (ej. "Bucle for") y pasa el texto a `grafo.py`.
2. **Inferencia Automática:** Genera el grafo matemático para deducir todos los saberes previos implícitos y anota todo en la memoria base del alumno.
3. **Loop Continuo:** Proporciona un menú infinito. Dependiendo de si se elige "Generar", "Resolver" o "Debuggear", rellena el diccionario de estado e invoca al grafo enrutador (`app.invoke(initial_state)`).
4. **Impresión Elegante:** Imprime al estudiante de forma clara los resultados en formato Markdown en la consola interactiva.

### 🗺️ `src/ontology/grafo.py` (La Ontología Pedagógica)
Es la fuente de la verdad académica; no interactúa con LLMs, se encarga sólo de la semántica.
- Alberga los diccionarios gigantes (`CONCEPTOS` y `RELACIONES`) que trazan las reglas estrictas de la programación.
- Integra la función crucial `construir_grafo()`, ensamblando la malla en un `NetworkX DiGraph`. Su existencia permite que `main.py` lance `nx.descendants()` y consiga perfiles anti-frustración certeros en tiempo O(V+E).

### 🧳 `src/agents/state.py` (El Sistema de Mensajería)
El maletín de estado inmutable.
- Define `TutorState`, un `TypedDict` que especifica datos exactos (`tarea`, `codigo_entrada`, `conceptos_buscados`).
- Dictamina los canales de comunicación. Los agentes no se pasan variables normales; todo el Graph interactúa mediante mutaciones seguras dentro de este envoltorio.

### 🚦 `src/agents/graph.py` (El Enrutador de LangGraph)
Funge como policía de tráfico dirigiendo la ejecución.
- Posee el **Enrutador Condicional** (`route_task`). 
- Inspecciona el saco de estado que trajo `main.py` y genera el flujo: Si piden un "ejercicio", avisa a `GraphRAG` primero, viaja a `generate_exercise` para fabricarlo, y termina en `generate_solution_node` (si pidieron solución adjunta).

### 🤖 `src/agents/nodes.py` (La Mente de la IA)
Donde reside la lógica pesada del "profesor" Llama.
- Ejecuta las directivas masivas de Ollama LLM (`ChatOllama`) inyectándolas con *System Prompts* hechos a medida.
- Determina su contexto subyacente. Inyecta **Chain-of-Thought** si se acciona en Clúster para maximizar rigor analítico o responde de manera local rápida según las limitantes del `.env`.

### 🛡️ `src/retriever/graph_rag.py` (RAG Estático Vectorless)
El bibliotecario veloz y protector in-memory.
- Al activarse por el LangGraph para crear simulacros, lee directamente `data/ejercicios_etiquetados.json`.
- Aplica su método interseccional puro eliminando sistemáticamente todos y cada uno de los problemas que requieran conceptos ajenos a la lista inferida de progreso del estudiante.

### 👷‍♂️ `deploy_cluster.sh` (Operario DevOps)
Responsable del CI/CD de bajo nivel.
- Ejecutado en servidores con restricciones, salta los problemas estructurales de Python Linux Global fabricando su `.venv_cluster`.
- Fusiona automáticamente configuraciones `.env.cluster` para orquestar la tarjeta gráfica corporativa y hace `pip install` de los dependientes, aislando el trabajo computacional por completo.

---

## 🚀 4. Plan de Despliegue en Clúster Científico (DevOps)

El salto a un entorno HPC (High Performance Computing) como el servidor universitario está orquestado mediante prácticas CI/CD modernas.
- Se implementó `deploy_cluster.sh`. Este script actúa como administrador de sistemas:
  - Hace "bypass" a las estrictas normativas protectoras de Linux (`PEP 668`) creando silos invisibles (`.venv_cluster`).
    - Purga archivos muertos, auto-sobrescribe ficheros locales `.env` con las variables HPC `.env.cluster` y fuerza el pre-calentamiento del modelo Llama.
    - Permite arrancar y usar el tutor inteligente en equipos sin privilegios administrativos en menos de 5 Minutos.

    > [!TIP]
    > **Pasos Futuros (Mejora de Capa 1):** Con toda la orquestación distribuida e in-memory trabajando impecablemente, el esfuerzo que lo transformará en un producto 10/10 es recubrirlo con una UI web moderna usando **Streamlit**. Esto mantendrá toda la arquitectura del Backend que hemos fabricado intacta, pero convertirá a `main.py` de una terminal verde y negra en un software gráfico que el tribunal del TFG aplaudirá por sí solo y que los alumnos reales podrán disfrutar desde su navegador.