# 🧪 PROMPT DE IMPLEMENTACIÓN: SCRIPT DE EVALUACIÓN MASIVA (BENCHMARKING)

Vamos a crear un entorno de laboratorio aislado para evaluar científicamente todos los modelos open-source disponibles usando nuestro motor RAG In-Memory. Esta métrica es vital para la memoria del TFG.

Por favor, crea un nuevo archivo en `src/evaluation/benchmark.py` respetando el principio de "Separation of Concerns" (no modifiques `main.py` ni el flujo del Tutor).

## 1. ESTRUCTURA DEL LABORATORIO
- **Lista de Modelos:** Define un array en Python con los modelos a evaluar: `MODELOS_A_TESTEAR = ["llama3.1:8b", "qwen2.5-coder:7b", "gemma2:9b", "mistral:7b", "phi3.5"]`.
- **Casos de Prueba:** Crea un mock de `Golden Dataset` en memoria (una lista de diccionarios) con 3 casos de prueba base (ej. Petición de un ejercicio de Bucles, Petición de un ejercicio de Recursividad).

## 2. EL MOTOR DE BENCHMARK (`benchmark.py`)
Implementa un script asíncrono que haga lo siguiente:
1. Iterar sobre cada modelo de la lista `MODELOS_A_TESTEAR`.
2. Por cada modelo, iterar sobre los casos del Golden Dataset.
3. Instanciar dinámicamente tu `ChatOllama` inyectando el modelo correspondiente en ese momento.
4. Ejecutar el flujo de generación del ejercicio (puedes instanciar una versión reducida de LangGraph o llamar directamente al generador y al Senado).
5. Medir el **tiempo de ejecución** (latencia) de cada generación.
6. Contar cuántos **intentos del Senado** hicieron falta para aprobarlo.

## 3. EXPORTACIÓN DE RESULTADOS
- El script debe recolectar todos los datos (Modelo, Caso de Prueba, Tiempo de Respuesta, Intentos del Senado, Ejercicio Generado).
- Al finalizar, debe exportar un archivo `resultados_benchmark.csv` usando la librería `csv` o `pandas`.

**No instales librerías de evaluación externas complejas todavía (como Ragas o DeepEval).** Por ahora, mediremos la Latencia y la Tasa de Rechazo del Senado como métricas principales de rendimiento. Escribe el código de `benchmark.py`.