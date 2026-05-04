# 🧠 Tutor Inteligente Multi-Agente (Graph RAG + LangGraph)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)](https://python.langchain.com/docs/langgraph/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-white.svg)](https://ollama.com/)
[![NetworkX](https://img.shields.io/badge/Ontology-NetworkX-green.svg)](https://networkx.org/)

Este repositorio contiene el código fuente de un **Sistema de Aprendizaje Adaptativo**. Es una arquitectura de Inteligencia Artificial que actúa como tutor experto de programación en Python, utilizando grafos de conocimiento in-memory y orquestación multi-agente con tolerancia a fallos.

---

## 🏛️ Arquitectura del Sistema

El sistema abandona el enfoque clásico de un "chatbot" tradicional para implementar un **Grafo Acíclico Dirigido (DAG)** mediante LangGraph. Esto permite delegar tareas específicas a distintos agentes especializados:

1. **RAG Ontológico In-Memory (`NetworkX`)**: Modela el plan de estudios de programación como un grafo dirigido de prerrequisitos. Impide estrictamente que el LLM utilice o enseñe conceptos que superen el "frente de aprendizaje" actual del alumno.
2. **Agente Generador (`qwen2.5-coder:32b`)**: Lee el contexto recuperado por el RAG y redacta un borrador pedagógico.
3. **El Senado Académico (BFT)**: Implementa Tolerancia a Fallos Bizantinos (Byzantine Fault Tolerance). Tres agentes jueces evalúan simultáneamente el borrador mediante "Majority Voting" (voto por mayoría) asegurando que el ejercicio respeta la dificultad y el estilo exigido.
4. **Debugger Determinista**: Un agente calibrado con `temperature=0.0` para buscar errores lógicos en el código del alumno con exactitud matemática.

---

## 🚀 Despliegue en Clúster (HPC / Servidores Universitarios)

Este proyecto está diseñado para ser desplegado en entornos sin permisos de administrador (Rootless) como clústeres universitarios. 

### 1. Requisitos Previos
No es necesario tener Ollama instalado a nivel de sistema. El script de arranque lo instalará en el espacio de usuario local `~/.local`.

### 2. Arranque Seguro (One-Click Deploy)
Clona este repositorio en tu clúster y ejecuta el script de orquestación principal:
```bash
git clone https://github.com/Jantoniio3/TFG
cd TFG
bash start.sh
```

**¿Qué hace `start.sh` de forma automática?**
- Verifica e instala la infraestructura LLM (Ollama) si no existe.
- Purga procesos zombie de GPU (evita colisión de puertos).
- Sincroniza variables de entorno (`cp .env.cluster .env`).
- Levanta el servidor LLM y descarga el modelo preconfigurado de 32 Billones de parámetros.
- Arranca el CLI del Tutor Inteligente.

---

## 💻 Configuración Local (Windows / Mac)

Si deseas correr el proyecto en tu máquina local para desarrollo:

1. Instala dependencias:
```powershell
pip install -r requirements.txt
```
2. Asegúrate de tener Ollama levantado localmente en el puerto `11434`.
3. Ejecuta el archivo principal:
```powershell
python main.py
```

---

## 🧪 Laboratorio de Benchmarking

El sistema incluye un evaluador dinámico para validar la capacidad matemática y de salida estructurada (JSON estricto) de los modelos descargados en el clúster, justificando así la elección tecnológica del Senado:

```bash
python src/evaluation/model_evaluator.py
```

---

## 📌 Configuración de VRAM (A40 GPU)
En el archivo `.env.cluster` se configura la gestión agresiva de VRAM:
- **`OLLAMA_MODEL`**: `qwen2.5-coder:32b` (Modelo experto en código que pesa ~19GB).
- **`NUM_CTX`**: `65536`. Dado que la A40 cuenta con 48GB, se amplía el contexto de ejecución a 64K tokens para permitir la votación asíncrona concurrente de 3 jueces en el Senado sin incurrir en VRAM Thrashing.

> **Nota:** Todos los módulos internos aplican una "Regla Estricta de Confinamiento de Conocimiento" que prohíbe pedagógicamente sugerir bibliotecas (`math`, `collections`, etc.) a alumnos que no han alcanzado dicho nodo en el grafo.