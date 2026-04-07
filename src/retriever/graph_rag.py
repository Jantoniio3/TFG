import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.database.neo4j_client import Neo4jClient

class GraphRAG:
    def __init__(self):
        self.client = Neo4jClient()
        
    def retrieve_valid_exercises(self, conceptos_buscados, conceptos_vistos, dificultad_deseada=None):
        """
        Recupera ejercicios que evalúan EXACTAMENTE los conceptos buscados (o un subconjunto)
        y NINGÚN concepto que no esté en la lista de conceptos_vistos.
        """
        
        # Consulta avanzada Cypher:
        # 1. Obtenemos ejercicios que evalúan AL MENOS UNO de los conceptos_buscados
        # 2. MATCH adicional para recolectar TODOS los conceptos de ese ejercicio
        # 3. Y filtramos: TODOS los conceptos evaluados deben estar dentro de la lista de conceptos_vistos.
        
        query = """
        MATCH (e:Ejercicio)-[:EVALUA]->(cb:Concepto)
        WHERE cb.nombre IN $buscados
        
        // Recogemos todos los conceptos de este ejercicio
        MATCH (e)-[:EVALUA]->(ctodos:Concepto)
        WITH e, collect(ctodos.nombre) as conceptos_del_ejercicio
        
        // El paso clave pedagógico: all(x IN collection WHERE condition)
        WHERE all(x IN conceptos_del_ejercicio WHERE x IN $vistos)
        """
        
        if dificultad_deseada:
            query += "\nAND e.dificultad = $dificultad"
            
        query += "\nRETURN e.id as id, e.enunciado as enunciado, e.dificultad as dificultad, conceptos_del_ejercicio LIMIT 5"
        
        params = {
            "buscados": conceptos_buscados,
            "vistos": conceptos_vistos
        }
        if dificultad_deseada:
            params["dificultad"] = dificultad_deseada
            
        try:
            resultados = self.client.execute_query(query, params)
            # Transformamos los Record de Neo4j en diccionarios
            return [{"id": r["id"], "enunciado": r["enunciado"], "dificultad": r["dificultad"], "conceptos": r["conceptos_del_ejercicio"]} for r in resultados]
        except Exception as e:
            print(f"Error consultando el grafo: {e}")
            return []

    def close(self):
        self.client.close()

if __name__ == "__main__":
    rag = GraphRAG()
    # Simulación de un alumno con conocimientos basales
    vistos = ["Algoritmo", "Programa", "Variable", "Función", "Argumento", "Operador"]
    buscados = ["Variable", "Función"]
    
    print(f"Buscando ejercicios sobre {buscados} con conocimientos limitados a {vistos}...")
    res = rag.retrieve_valid_exercises(buscados, vistos)
    if not res:
        print("Graph RAG no devolvió resultados (es lo esperado si los ejercicios evaluaban conceptos como 'Diccionario' o 'Recursividad' que el alumno no conoce).")
    for r in res:
        print(f"Encontrado: {r['id']} - (Conceptos: {r['conceptos']})")
    rag.close()
