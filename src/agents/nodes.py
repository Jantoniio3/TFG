import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.retriever.graph_rag import GraphRAG

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

def get_llm():
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    num_ctx = int(os.getenv("NUM_CTX", "16384"))
    env = os.getenv("ENVIRONMENT", "local")
    
    if env == "cluster":
        # Mensaje opcional para que se vea en los logs de Streamlit/Consola que se activa la A40
        pass
        
    return ChatOllama(model=model_name, num_ctx=num_ctx, temperature=0.7)

def get_llm_deterministic():
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    num_ctx = int(os.getenv("NUM_CTX", "16384"))
    return ChatOllama(model=model_name, num_ctx=num_ctx, temperature=0.0)

def router_node(state):
    return state

def retrieve_exercises(state):
    rag = GraphRAG()
    ejercicios = rag.retrieve_valid_exercises(state.get("conceptos_buscados", []), state.get("alumno_historial", []))
    rag.close()
    return {"ejercicios_contexto": ejercicios}

def generate_exercise(state):
    llm = get_llm()
    buscados = ', '.join(state.get('conceptos_buscados', []))
    vistos = ', '.join(state.get('alumno_historial', []))
    contexto = "\n".join([f"Id: {e['id']} - Dificultad: {e['dificultad']}\nEnunciado: {e['enunciado']}" for e in state.get("ejercicios_contexto", [])])
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"Eres un profesor experto de programación. Tu objetivo es generar un ejercicio de código en {lenguaje}."
    user_prompt = f"""Restricciones Críticas:
1. El alumno solo conoce estos conceptos: {vistos}. NO incluyas ni uses conceptos que no estén en esta lista.
2. El ejercicio debe enfocarse en poner en práctica principalmente estos conceptos: {buscados}.
3. Dificultad deseada: {state.get('dificultad', 'Media')}.

Contexto de ejercicios similares para inspiración:
{contexto}

Devuelve ÚNICAMENTE el texto en formato Markdown con el enunciado completo del nuevo ejercicio."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return {"enunciado_generado": response.content}

def generate_solution_node(state):
    llm = get_llm()
    enunciado = state.get("enunciado_generado", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"""Eres el profesor que ha escrito este ejercicio. Por favor, resuelve el ejercicio aportando:
1. El código en {lenguaje} correcto.
2. Una explicación pedagógica de cómo funciona el código y por qué se resuelve así.
Devuelve el resultado en Markdown, de forma clara y unificada."""
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Este es el enunciado del ejercicio:\n{enunciado}")
    ])
    
    return {"resultado_codigo": response.content}

def solve_node(state):
    llm = get_llm()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"Eres un tutor experto. Tu objetivo es explicar qué hace este código en {lenguaje} proporcionado de forma pedagógica, o explicar su lógica general, y proponer un código mejorado si ves áreas de mejora. Devuelve la respuesta en Markdown."
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}

def find_bugs_node(state):
    llm = get_llm_deterministic()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"Eres un debugger experto en {lenguaje}. Tu objetivo es encontrar fallos lógicos o sintácticos en el código proporcionado. Explica dónde están los errores, por qué ocurren y proporciona la versión corregida. Sé muy metódico. Devuelve el resultado en Markdown."
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}
