import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.neo4j_client import Neo4jClient
from src.etl.rubric_classifier import classify_exercise
try:
    from langchain_community.llms import Ollama
    llm = Ollama(model="llama3.1")
except:
    llm = None

def ingest_exercises():
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ejercicios_parseados.json')
    if not os.path.exists(json_path):
        print("No se encontró el archivo de ejercicios parseados.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        ejercicios = json.load(f)

    client = Neo4jClient()

    # Procesamos solo 3 ejercicios por ahora para probar rápidamente 
    # sin tener horas de inferencia en local. (Se puede quitar el [:3] en producción)
    ejercicios_a_procesar = ejercicios[:3]
    
    # Ingestar manual desde cuaderno 2 anotado.txt si fuesen los primeros. 
    # Usaremos el LLM en su lugar como pide el requerimiento.

    print(f"Procesando e ingestando {len(ejercicios_a_procesar)} ejercicios usando Ollama...")
    for ej in ejercicios_a_procesar:
        print(f"Clasificando {ej['id']}...")
        calificacion = classify_exercise(ej['enunciado'][:500] + "...", llm=llm)
        
        # 1. Crear el Nodo de Ejercicio
        query_ejercicio = """
        MERGE (e:Ejercicio {id: $id})
        SET e.enunciado = $enunciado,
            e.estado = $estado,
            e.contenido = $contenido,
            e.dificultad = $dificultad,
            e.tipo = $tipo
        """
        params = {
            "id": ej['id'],
            "enunciado": ej['enunciado'],
            "estado": ej['estado'],
            "contenido": calificacion.get("contenido", ""),
            "dificultad": calificacion.get("dificultad", ""),
            "tipo": calificacion.get("tipo", "")
        }
        client.execute_write(query_ejercicio, params)

        # 2. Linkear a los conceptos de la Calificacion con relacion EVALUA
        conceptos = calificacion.get("conceptos_evaluados", [])
        for concepto in conceptos:
            query_link = """
            MATCH (e:Ejercicio {id: $id_ej})
            MATCH (c:Concepto {nombre: $nombre_concepto})
            MERGE (e)-[r:EVALUA {peso: 2}]->(c)
            """
            client.execute_write(query_link, {
                "id_ej": ej['id'],
                "nombre_concepto": concepto
            })
            print(f"  -> Link creado: ({ej['id']}) -[:EVALUA]-> ({concepto})")

    client.close()
    print("Ingesta completada.")

if __name__ == "__main__":
    ingest_exercises()
