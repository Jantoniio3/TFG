import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.retriever.graph_rag import GraphRAG

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

import asyncio
from pydantic import BaseModel, Field

class SenateVote(BaseModel):
    aprueba: bool = Field(description="True si el ejercicio es adecuado, False si no cumple los requisitos.")
    critica: str = Field(description="Breve razonamiento o crítica de tu voto.")

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
    env = os.getenv("ENVIRONMENT", "local")
    if env == "cluster":
        print("[⚡ CLUSTER MODE] Usando GPU A40 / Llama-3.1 70B determinista para mayor exactitud.")
    return ChatOllama(model=model_name, num_ctx=num_ctx, temperature=0.0)

def get_cluster_prompt_suffix():
    env = os.getenv("ENVIRONMENT", "local")
    if env == "cluster":
        return "\n\n[INSTRUCCIÓN AVANZADA CLÚSTER A40]: Dado que cuentas con alta capacidad computacional y de contexto, por favor utiliza 'Chain of Thought' (piensa paso a paso). Argumenta exhaustivamente tus decisiones, provee consideraciones pedagógicas o de rendimiento sumamente profundas, y genera respuestas del más alto nivel técnico y descriptivo disponible."
    return ""

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
    
    reintentos = state.get("reintentos", 0)
    criticas = state.get("criticas_senado", "")
    
    system_prompt = f"Eres un profesor experto de programación. Tu objetivo es generar un ejercicio de código en {lenguaje}." + get_cluster_prompt_suffix()
    user_prompt = f"""Restricciones Críticas:
1. El alumno solo conoce estos conceptos: {vistos}. NO incluyas ni uses conceptos que no estén en esta lista.
2. El ejercicio debe enfocarse en poner en práctica principalmente estos conceptos: {buscados}.
3. Dificultad deseada: {state.get('dificultad', 'Media')}.

Contexto de ejercicios similares para inspiración:
{contexto}
"""
    if reintentos > 0 and criticas:
        user_prompt += f"\nATENCIÓN: Este es el intento número {reintentos + 1}. El Senado rechazó tu ejercicio anterior con las siguientes críticas:\n{criticas}\nPOR FAVOR, CORRIGE EL EJERCICIO TENIENDO EN CUENTA ESTE FEEDBACK.\n"

    user_prompt += "\nDevuelve ÚNICAMENTE el texto en formato Markdown con el enunciado completo del nuevo ejercicio."

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return {"ejercicio_generado": response.content}

def senate_evaluation_node(state):
    print("\n⚖️ El Senado está debatiendo...")
    llm = get_llm().with_structured_output(SenateVote)
    
    ejercicio = state.get("ejercicio_generado", "")
    dificultad = state.get("dificultad", "Media")
    contexto = "\n".join([f"Enunciado: {e['enunciado']}" for e in state.get("ejercicios_contexto", [])])
    
    system_prompt = f"""Eres un juez estricto en el Senado Académico.
Debes evaluar el siguiente ejercicio generado por otro profesor.
Criterios estrictos:
1. ¿La dificultad del ejercicio coincide razonablemente con la pedida por el alumno ({dificultad})?
2. ¿El formato y estilo del ejercicio se parece a los ejercicios base extraídos del contexto?

Contexto de ejercicios base para guiar el estilo:
{contexto}

Evalúa estrictamente si apruebas o no el ejercicio y da una breve crítica.""" + get_cluster_prompt_suffix()

    user_prompt = f"Ejercicio a evaluar:\n{ejercicio}"

    async def get_vote():
        return await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

    async def run_senate():
        return await asyncio.gather(get_vote(), get_vote(), get_vote())

    try:
        try:
            loop = asyncio.get_running_loop()
            # Si hay loop, creamos tarea para evitar RuntimeError
            votes = asyncio.run_coroutine_threadsafe(run_senate(), loop).result()
        except RuntimeError:
            votes = asyncio.run(run_senate())
    except Exception as e:
        print(f"[!] Aviso: fallback a votación síncrona por error asíncrono ({e})")
        votes = [llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]) for _ in range(3)]

    votos_favor = sum(1 for v in votes if getattr(v, "aprueba", False))
    votos_contra = 3 - votos_favor
    
    criticas_list = [f"Juez {i+1} ({'Aprueba' if getattr(v, 'aprueba', False) else 'Rechaza'}): {getattr(v, 'critica', '')}" for i, v in enumerate(votes)]
    criticas_str = "\n".join(criticas_list)
    
    if votos_favor >= 2:
        print(f"🏛️ Votación del Senado: {votos_favor} a favor, {votos_contra} en contra. ¡Ejercicio Aprobado!")
        return {
            "enunciado_generado": ejercicio,
            "criticas_senado": "" 
        }
    else:
        print(f"🏛️ Votación del Senado: {votos_favor} a favor, {votos_contra} en contra. Ejercicio Rechazado.")
        reintentos_actuales = state.get("reintentos", 0)
        return {
            "reintentos": reintentos_actuales + 1,
            "criticas_senado": criticas_str
        }

def generate_solution_node(state):
    llm = get_llm()
    enunciado = state.get("enunciado_generado", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"""Eres el profesor que ha escrito este ejercicio. Por favor, resuelve el ejercicio aportando:
1. El código en {lenguaje} correcto.
2. Una explicación pedagógica de cómo funciona el código y por qué se resuelve así.
Devuelve el resultado en Markdown, de forma clara y unificada.""" + get_cluster_prompt_suffix()
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Este es el enunciado del ejercicio:\n{enunciado}")
    ])
    
    return {"resultado_codigo": response.content}

def solve_node(state):
    llm = get_llm()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"Eres un tutor experto. Tu objetivo es explicar qué hace este código en {lenguaje} proporcionado de forma pedagógica, o explicar su lógica general, y proponer un código mejorado si ves áreas de mejora. Devuelve la respuesta en Markdown." + get_cluster_prompt_suffix()
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}

def find_bugs_node(state):
    llm = get_llm_deterministic()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    
    system_prompt = f"Eres un debugger experto en {lenguaje}. Tu objetivo es encontrar fallos lógicos o sintácticos en el código proporcionado. Explica dónde están los errores, por qué ocurren y proporciona la versión corregida. Sé muy metódico. Devuelve el resultado en Markdown." + get_cluster_prompt_suffix()
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}
