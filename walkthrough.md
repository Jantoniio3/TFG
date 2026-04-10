🎓 Walkthrough Arquitectónico: Tutor Inteligente (TFG)
Este documento es un resumen técnico y analítico exhaustivo de todo el proyecto del Sistema de Aprendizaje Inteligente, listo para usarse como base para la memoria de tu TFG o para preparar su defensa.

> [!NOTE]
> **Visión General del Sistema:** El proyecto consiste en un Tutor Inteligente Interactivo basado en una arquitectura Multi-Agente (LangGraph) y un motor In-Memory RAG. Sirve como ayudante a estudiantes de programación mediante la generación de ejercicios adaptativos infiriendo sus conocimientos base en tiempo real para evitar frustración.

## 🏗️ 1. Arquitectura Central

### 1.1 Modelo LLM Desacoplado (Ollama)
El sistema no depende de costosas APIs externas (como OpenAI), mejorando enormemente su impacto open-source y su privacidad en entornos educativos.
- Se utiliza `langchain-ollama` para instanciar dinámicamente modelos de generación.
- **Hot-Swapping**: mediante el `.env`, el sistema migra suavemente entre un entorno local portátil (`llama3.1:8b`) hacia entornos de supercómputo (Clúster A-40) corriendo gigantes de 70b parámetros para capacidades de inferencia masivas.

### 1.2 Grafo de Conocimiento In-Memory (NetworkX)
Tras un pivote arquitectónico, **se eliminó la dependencia de bases de datos externas (Neo4j)**, logrando un sistema mucho más ligero, distribuible y veloz 100% en la memoria RAM:
- **Ontología en Código:** Toda la lógica de relaciones (`REQUIERE_PREVIO`, etc.) vive dictada en diccionarios dinámicos dentro de `src/ontology/grafo.py`. 
- **Sistema Anti-Alucinaciones Ultrasónico:** Cuando un estudiante indica parte de su currículo, `main.py` genera el grafo in-memory usando la librería matemática `networkx` e infiere todos sus ancestros usando `nx.descendants()`. Esto deduce sus competencias subyacentes sin ralentizaciones por red.
- **RAG Estático Vectorless:** El `GraphRAG` carga el dataset base `ejercicios_etiquetados.json` directamente a la memoria e implementa intersección lógica nativa de Python (`issubset()`) para inyectar solo casos compatibles.

### 1.3 Orquestación Multi-Agente (LangGraph)
Nuestra transición de una arquitectura estática (Scripts planos) al paradigma contemporáneo Multi-Agente proporciona un Grafo Aclítico Dirigido (DAG).
- En `graph.py` reside el enrutador (`router_node`).
- Según la intención (generar, resolver, debuggear) calculada, la carga se transfiere dinámicamente por la red neuronal del equipo multi-agente en `nodes.py`.
- **Clúster Prompting Dinámico**: Si el software detecta una NVIDIA A40 y modo clúster, los nodos cambian a modo "Chain of Thought" para explicar pedagogía y optimización algorítmica profunda automáticamente.

## 💻 2. Experiencia de Usuario (El Orquestador CLI)
El archivo `main.py` actúa como la interfaz robusta integrando toda la tecnología subyacente de forma ininterrumpida.

**Hitos del Flujo CLI:**
- **Perfiles Dinámicos de una sola Inyección**: Pregunta al usuario por 1 o 2 temas e infiere la curva entera de aprendizaje del alumno almacenándola en estado.
- **Internacionalización Lógica**: Pregunta dinámicamente el lenguaje a aprender (Python, Java, C++). Todos los *prompts* del sistema están pre-inyectados para adaptarse.
- **Ciclo Sostenido**: Muestra enunciados, explicaciones y correcciones interactivas soportando entradas crudas multilínea de largos bloques de código de los alumnos.

## 🚀 3. Metodología DevOps / Localización
Se ha configurado un ambiente de Infraestructura Desacoplada sin ataduras pesadas.

- **Local (Capa de Desarrollo)**: Archivo `.env` con consumos menores de memoria unificada (`NUM_CTX=4096`).
- **Producción/Staging (Clúster Universidad)**: `deploy_cluster.sh` autónomo con `externally-managed-environment` by-passed vía Entornos Virtuales Aislados, con `.env.cluster` pidiendo altos niveles de contexto `NUM_CTX`.

> [!TIP]
> **Pasos Futuros:** Habiendo independizado el core multi-agente en memoria RAM local sin bases de datos ajenas, la escalabilidad final se concentrará puramente en reemplazar la Capa CLI (`main.py`) por un despliegue gráfico moderno con la librería `Streamlit` para encapsular las interacciones en una Interfaz de Usuario (UI) reactiva, permitiendo al tribunal o usuarios interactuar desde sus navegadores web de forma elegante.