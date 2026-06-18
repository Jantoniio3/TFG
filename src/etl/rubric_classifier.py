import json
import re
import os
from langchain_community.llms import Ollama

def classify_exercise(exercise_text, exercise_id="E000", llm=None):
    if llm is None:
        try:
            llm = Ollama(model="llama3.1")
        except Exception:
            llm = None
            
    prompt = f"""
    Eres un asistente experto en pedagogía y programación. 
    Tu tarea es parsear y clasificar el siguiente ejercicio de programación en Python según el formato requerido.
    
    Ejercicio en bruto:
    {exercise_text}
    
    FORMATO JSON REQUERIDO:
    Devuelve ÚNICAMENTE un objeto JSON válido con exactamente estas claves:
    - "id": "{exercise_id}"
    - "difficulty": "fácil", "media" o "difícil".
    - "domain": El dominio general (ej. "Introducción", "Estructuras de datos", "Subprogramación", "Estructuras de control", etc.)
    - "primary_concept": El concepto principal evaluado.
    - "concepts": Lista de strings con los conceptos evaluados (ej. ["Variable", "Bucle for"]).
    - "statement": El enunciado limpio del ejercicio (sin la solución).
    - "starter_code": Código inicial si se proporciona, sino null.
    - "solution": Código de la solución si está en el texto bruto, sino null.
    
    Asegúrate de responder SOLO con el objeto JSON. Sin explicaciones previas ni texto posterior.
    """
    
    if llm is None:
        return _mock_response(exercise_id)
    
    try:
        response = llm.invoke(prompt)
        match = re.search(r'(\{.*\})', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Intentar parsear directo si no hay regex hit
        return json.loads(response)
    except Exception as e:
        print(f"Error parseando la salida del LLM para {exercise_id}: {e}")
        return _mock_response(exercise_id)

def _mock_response(exercise_id):
    # Mock base para que no bloquee la ejecución si falla
    return {
        "id": exercise_id,
        "difficulty": "media",
        "domain": "Subprogramación",
        "primary_concept": "Función",
        "concepts": ["Función", "Variable local"],
        "statement": "Este es un enunciado de prueba extraído del mock.",
        "starter_code": None,
        "solution": "def prueba():\n    pass"
    }

if __name__ == "__main__":
    # Actualizado para iterar sobre los ejercicios parseados y generar el formato dataset
    input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ejercicios_parseados.json')
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nuevo_exercises_dataset.json')
    
    if os.path.exists(input_path):
        print(f"Procesando {input_path}...")
        with open(input_path, 'r', encoding='utf-8') as f:
            ejercicios_raw = json.load(f)
            
        try:
            llm = Ollama(model="llama3.1")
        except Exception:
            llm = None
            
        resultados = {}
        for ej in ejercicios_raw:
            eid = ej.get('id', 'E000')
            print(f"Clasificando {eid}...")
            res = classify_exercise(ej['enunciado'], exercise_id=eid, llm=llm)
            resultados[res['id']] = res
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
            
        print(f"Proceso finalizado. Guardado en {output_path}")
    else:
        print(f"No se encontró el archivo de entrada: {input_path}")
