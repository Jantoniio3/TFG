# 🔄 PIVOTE ARQUITECTÓNICO CRÍTICO: DE NEO4J A NETWORKX (IN-MEMORY GRAPH RAG)

Hemos decidido pivotar nuestra arquitectura de base de datos. Para maximizar la portabilidad del TFG y eliminar la dependencia de contenedores externos, **vamos a abandonar Neo4j por completo y migrar a un motor de grafos 100% en memoria usando `networkx`**. 

He proporcionado un nuevo archivo llamado `grafo.py` que contiene la ontología completa, las relaciones estructuradas y los métodos de navegación del grafo.

Por favor, refactoriza el proyecto aplicando los siguientes cambios estrictos:

## 1. LIMPIEZA DE DEPENDENCIAS (DROP NEO4J)
- **Eliminar:** Borra el archivo `src/database/neo4j_client.py` (o equivalente).
- **Entorno:** Elimina todas las variables relacionadas con Neo4j (`NEO4J_URI`, etc.) del archivo `.env` y de la configuración.
- **Requirements:** Asegúrate de que `neo4j` ya no esté en `requirements.txt` y de que `networkx` sí esté.

## 2. INTEGRACIÓN DEL NUEVO MOTOR (grafo.py)
- Mueve el archivo proporcionado `grafo.py` a la carpeta `src/graph/` (o `src/database/` si prefieres mantener esa nomenclatura).
- Este archivo será a partir de ahora la **Única Fuente de Verdad (SSOT)** para la teoría y las validaciones de prerrequisitos.

## 3. REFACTORIZACIÓN DEL RETRIEVER (GRAPH RAG)
El nodo `retriever_node` (y cualquier lógica de búsqueda) ya no ejecutará consultas Cypher. Ahora debe usar las funciones nativas de `grafo.py`:
- **Filtro Anti-Frustración:** Cuando el alumno busque ejercicios de un concepto, debes verificar si ese concepto está desbloqueado usando la función `frente_aprendizaje(conceptos_vistos)`. Si el concepto pedido no está en el frente ni en los dominados, el sistema debe avisar de que faltan prerrequisitos.
- **Enriquecimiento del Prompt:** Al recuperar el contexto para pasárselo al LLM (Generador), utiliza las funciones `casos_especiales(concepto)` y `combinaciones_naturales(concepto)`. Inyecta estas listas en el prompt del LLM para que las use como inspiración al redactar el enunciado del ejercicio.

## 4. GESTIÓN DE LOS EJERCICIOS (JSON)
Como ya no tenemos Neo4j para guardar los nodos de tipo `Ejercicio`, debes cargar el archivo `ejercicios_troceados.json` (o equivalente) directamente en memoria al iniciar la aplicación (ej. en un diccionario de Python o un DataFrame de Pandas ligero).
- Para buscar un ejercicio candidato, filtra la lista de ejercicios en memoria buscando aquellos cuya lista de `conceptos_evaluados` sea un subconjunto de `conceptos_vistos + concepto_objetivo`.

## 5. IMPACTO EN EL RESTO DEL FLUJO
- El Enrutador (Router) y los nodos del LLM (`solve_node`, `find_bugs_node`) no cambian su lógica, pero los contextos de teoría que reciban ahora provendrán de llamadas a `grafo.py` en lugar de la base de datos externa.
- Actualiza la interfaz interactiva (`main.py`) para que la lista de conceptos a elegir se cargue haciendo `from src.graph.grafo import DOMINIOS, CONCEPTOS`.

**Procede paso a paso: primero limpia Neo4j, luego integra `grafo.py`, y finalmente refactoriza el Retriever para usar la lógica de NetworkX.**