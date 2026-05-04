"""Módulo de Recuperación Aumentada por Grafo (Graph RAG).

Este módulo se encarga de recuperar los ejercicios del dataset JSON In-Memory,
aplicando filtrados estrictos basados en el frente de aprendizaje del alumno.
"""

import os
import json
import random

class GraphRAG:
    """Clase para la recuperación y filtrado de ejercicios (RAG In-Memory).
    
    Carga la base de datos de ejercicios etiquetados y permite extraer 
    únicamente aquellos que cumplen con las restricciones pedagógicas.
    """

    def __init__(self):
        """Inicializa el motor RAG cargando el dataset local JSON."""
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ejercicios_etiquetados.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                self.ejercicios = json.load(f)
        else:
            self.ejercicios = []
            print(f"[!] No se encontró '{json_path}'. El RAG está vacío.")
            
    def retrieve_valid_exercises(self, conceptos_buscados: list[str], conceptos_vistos: list[str], dificultad_deseada: str = None) -> list[dict]:
        """Recupera los ejercicios que encajan perfectamente con el perfil del alumno.
        
        Args:
            conceptos_buscados: Lista de conceptos en los que se debe enfocar el ejercicio.
            conceptos_vistos: Lista completa del historial de conceptos dominados por el alumno.
            dificultad_deseada: Filtro opcional por nivel de dificultad ("Fácil", "Media", "Difícil").
            
        Returns:
            list[dict]: Lista con los 5 mejores ejercicios que cumplen TODAS las restricciones.
        """
        valid_exercises = []
        set_buscados = set(conceptos_buscados)
        set_vistos = set(conceptos_vistos)

        for ej in self.ejercicios:
            evaluados = set(ej.get("conceptos_evaluados", []))
            
            # 1. El ejercicio debe cubrir al menos uno de los conceptos buscados
            if set_buscados and not (evaluados & set_buscados):
                continue
                
            # 2. TODOS los conceptos que evalúa el ejercicio deben haber sido ya vistos por el alumno
            if not evaluados.issubset(set_vistos):
                continue
                
            # 3. Filtrado por dificultad
            if dificultad_deseada and ej.get("dificultad") != dificultad_deseada:
                continue
                
            valid_exercises.append({
                "id": ej.get("id"),
                "enunciado": ej.get("enunciado"),
                "solucion": ej.get("solucion", ""),
                "dificultad": ej.get("dificultad"),
                "conceptos": list(evaluados)
            })

        # Rotar aleatoriamente y devolver top 5
        random.shuffle(valid_exercises)
        return valid_exercises[:5]

    def close(self):
        """Método de limpieza por compatibilidad (vacío al operar In-Memory)."""
        pass

if __name__ == "__main__":
    rag = GraphRAG()
    vistos = ["Algoritmo", "Programa", "Variable", "Función", "Argumento", "Operador", "Parámetro"]
    buscados = ["Función", "Variable"]
    
    print(f"Buscando ejercicios sobre {buscados} con conocimientos limitados a {vistos}...")
    res = rag.retrieve_valid_exercises(buscados, vistos, "Fácil")
    if not res:
        print("Graph RAG no devolvió resultados.")
    for r in res:
        print(f"Encontrado: {r['id']} - (Conceptos: {r['conceptos']})")
