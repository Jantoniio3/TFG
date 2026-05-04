import json
import re
from langchain_community.llms import Ollama

def classify_exercise(exercise_text, llm=None):
    if llm is None:
        try:
            llm = Ollama(model="llama3.1")
        except Exception:
            llm = None
            
    prompt = f"""
    Eres un asistente experto en pedagogía y programación. 
    Tu tarea es clasificar el siguiente ejercicio de programación en Python según una rúbrica estricta.
    
    Ejercicio:
    {exercise_text}
    
    RÚBRICA Y FORMATO JSON REQUERIDO:
    Devuelve ÚNICAMENTE un JSON válido con estas claves:
    - "contenido": Elige una: ["Muy sencillo", "Corto", "Condicional-Iteracion simple", "Colecciones y slicing", "Composición", "Algorítmico clásico", "Recursivo", "Mixto"]
    - "dificultad": Elige una: ["Nivel Fácil", "Nivel Medio", "Nivel Difícil", "Nivel Muy Difícil"]
    - "tipo": Elige una: ["Rellenar huecos", "Completar código", "Encontrar errores", "Corregir errores", "Predecir la salida", "Determinar si el código se ejecuta correctamente", "Reescribir código (Refactoring)", "Diseñar un script / programa desde cero", "Razonamiento sobre casos de prueba"]
    - "conceptos_evaluados": Una lista de nombres EXACTOS de conceptos de teoría de programación en Python (ej. "Algoritmo", "Bucle for", "Variable", "Tipo de dato").
    
    Asegúrate de responder SOLO con el objeto JSON. Sin explicaciones previas ni texto posterior.
    """
    
    if llm is None:
        return _mock_response()
    
    try:
        response = llm.invoke(prompt)
        match = re.search(r'(\{.*\})', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Intentar parsear directo si no hay regex hit
        return json.loads(response)
    except Exception as e:
        print(f"Error parseando la salida del LLM: {e}")
        return _mock_response()

def _mock_response():
    # Mock base para que no bloquee la ejecución si falla
    return {
        "contenido": "Mixto",
        "dificultad": "Nivel Medio",
        "tipo": "Diseñar un script / programa desde cero",
        "conceptos_evaluados": ["Programa", "Variable", "Función", "Argumento"] 
    }

if __name__ == "__main__":
    fake_ex = "Programa una función que sume dos números enteros y devuelva el resultado."
    print("Probando clasificación (asegúrate de que Ollama está corriendo con llama3.1)...")
    res = classify_exercise(fake_ex)
    print(json.dumps(res, indent=2, ensure_ascii=False))
