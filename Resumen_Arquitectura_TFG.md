# 🎓 Resumen del Proyecto: Sistema Inteligente de Aprendizaje Adaptativo (TFG)

Este documento detalla la arquitectura, componentes y flujos de trabajo del proyecto actual. Sirve como referencia técnica para la redacción de la memoria del TFG y futuras defensas académicas.

## 1. Visión General
El proyecto es un **Tutor Inteligente por Consola (CLI)** diseñado para enseñar programación de forma adaptativa. A diferencia de un ChatGPT genérico, este sistema está estrictamente acotado cognitivamente: nunca evalúa ni propone al estudiante conceptos o estructuras de código que aún no haya estudiado, evitando así la frustración del alumno.

## 2. Tecnologías Principales
*   **Python 3**: Lenguaje base.
*   **LangChain / LangGraph**: Orquestación de agentes inteligentes y flujos lógicos en forma de Grafo Acíclico Dirigido (DAG).
*   **Ollama (Llama 3.1 8B / 32B)**: Motor de inferencia LLM ejecutado en local o en remoto.
*   **NetworkX**: Grafo In-Memory para la ontología de conceptos.
*   **ChromaDB**: Base de datos vectorial para recuperación semántica (RAG).

## 3. Arquitectura del Sistema

### 3.1. Ontología y Perfilado Cognitivo (Graph RAG)
El sistema mantiene un Grafo de Conocimiento donde los conceptos de programación están enlazados mediante relaciones semánticas (ej. `Bucle For` -REQUIERE_PREVIO-> `Variable`).
*   **Funcionamiento**: Cuando el alumno indica los conceptos punta de lanza que domina (ej. "Bucles"), el sistema navega hacia atrás por el grafo para inferir automáticamente todo su historial subyacente.
*   **Recuperación RAG**: El sistema filtra la base de datos de ejercicios (`exercises_dataset.json`) para devolver *solo* ejemplos que el alumno sea capaz de resolver, inyectándolos en el contexto del LLM.

### 3.2. Nodos Inteligentes (Agentes)
*   **Generador**: Un agente LLM creativo (Temp 0.7) que redacta ejercicios totalmente nuevos. Se le imponen 4 reglas críticas, incluyendo el confinamiento de conocimientos y la obligatoriedad de ser 100% original respecto a los ejemplos del RAG.
*   **Tutor Solucionador**: Resuelve el ejercicio generado aportando una explicación pedagógica acotada al nivel del alumno.
*   **Tutor Corrector (Modo Socrático)**: Lee código del alumno y explica qué hace, sugiriendo mejoras sin revelar conceptos futuros.
*   **Debugger**: Agente LLM Determinista (Temp 0.0) que localiza bugs de sintaxis y lógica en código proporcionado por el usuario.

### 3.3. Arquitecturas de Validación (Senado Académico)
Para mitigar las alucinaciones del Generador, el sistema cuenta con un "Senado" que audita la dificultad, pertinencia y originalidad del ejercicio antes de mostrárselo al estudiante.
*   **Opción 1 (Turbo)**: Sin Senado. Rápido, pero propenso a desviaciones.
*   **Opción 2 (Senado BFT - Byzantine Fault Tolerance)**: Ejecuta 3 jueces LLM independientes en paralelo (`asyncio.gather`). Requiere una votación binaria por mayoría (2/3) para aprobar.
*   **Opción 3 (Senado Reflexivo Secuencial - Calidad Máxima)**: Funciona como una cadena de montaje (Pipeline). 
    *   Juez 1 recibe la V1, hace una crítica y escupe la V2. 
    *   Juez 2 recibe la V2, hace crítica y escupe V3. 
    *   Juez 3 recibe la V3, aplica pulido final, da la nota final y escupe la V4. Si la nota es >= 8, se aprueba. Si no, se devuelve el histórico entero al Generador.

## 4. Diseño de Interfaz y Experiencia de Usuario (UX)
Al ser una aplicación de terminal, se ha puesto especial foco en la trazabilidad y la retroalimentación visual:
*   **Spinner Dinámico Async**: Reloj de arena (`⏳ La IA está razonando...`) en un hilo en segundo plano que avisa al usuario de que el clúster está operando, evitando la sensación de "pantalla congelada".
*   **Esquema de Colores ANSI**: 
    *   `Cyan`: Entradas del usuario.
    *   `Amarillo`: Preguntas y confirmaciones del sistema.
    *   `Verde`: Salidas limpias del sistema (soluciones, enunciados).
*   **Modo Desarrollador (Debug Terminal)**: Formatea en pantalla el proceso lógico del LLM dividiéndolo en:
    *   `Azul Oscuro`: Instrucciones del Sistema (`System Prompt`).
    *   `Cyan`: Datos dinámicos inyectados al prompt (`User Prompt`).
    *   `Verde Claro`: Volcado en crudo del JSON devuelto por la IA.
*   **Gestión de Logs**: Todo ejercicio o respuesta generada se guarda automáticamente en disco (`exercice.md` y `tutor_response.md`).

## 5. Escalabilidad y Despliegue
*   **Soporte Clúster GPU**: El sistema puede redirigir las cargas de inferencia al clúster de la universidad (Nvidia A40) estableciendo `ENVIRONMENT=cluster` y un túnel SSH, inyectando un prefijo lógico en los prompts para decirle al modelo que utilice toda su capacidad cognitiva (`Chain of Thought`).
