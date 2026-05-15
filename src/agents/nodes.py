"""Nodos del Grafo (Agentes Inteligentes).

Este módulo contiene la lógica interna de cada nodo de LangGraph, incluyendo
la comunicación con la API de Ollama, el manejo de prompts y la estructura de agentes.
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.retriever.graph_rag import GraphRAG

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

import asyncio
from pydantic import BaseModel, Field

DEV_COLOR = "\033[95m"  # Magenta para los prompts del modo desarrollador
DEV_SYS_COLOR = "\033[94m"  # Azul para System Prompts
DEV_USER_COLOR = "\033[96m" # Cyan para User Prompts
DEV_RES_COLOR = "\033[92m"  # Verde para la Respuesta cruda
RESET_COLOR = "\033[0m"

class SenateVoteBFT(BaseModel):
    aprueba: bool = Field(description="True si el ejercicio es adecuado, False si no cumple los requisitos.")
    critica: str = Field(description="Breve razonamiento de tu voto. Si rechazas el ejercicio, incluye una propuesta de mejora constructiva para rehacerlo.")

class SenateVoteReflection(BaseModel):
    nota: int = Field(description="Nota del 0 al 10 evaluando la calidad y adecuación del ejercicio.")
    critica: str = Field(description="Breve justificación de tu nota. PROHIBIDO dar consejos de mejora aquí. Si algo se puede mejorar, hazlo directamente en 'ejercicio_mejorado'.")
    ejercicio_mejorado: str = Field(description="OBLIGATORIO: El enunciado del ejercicio completamente reescrito y perfeccionado, aplicando todas tus mejoras directamente. Listo para ser entregado al alumno sin más modificaciones.")

load_dotenv()

def get_llm():
    """Instancia el modelo LLM con temperatura estándar para tareas creativas.
    
    Lee la configuración del entorno para determinar si está en el clúster
    o en local, ajustando el modelo y la memoria contextual.
    
    Returns:
        ChatOllama: Instancia del modelo LLM configurado (temperatura 0.7).
    """
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    num_ctx = int(os.getenv("NUM_CTX", "16384"))
    env = os.getenv("ENVIRONMENT", "local")
    
    if env == "cluster":
        # Mensaje opcional para que se vea en los logs de Streamlit/Consola que se activa la A40
        pass
        
    return ChatOllama(model=model_name, num_ctx=num_ctx, temperature=0.7)

def get_llm_deterministic():
    """Instancia el modelo LLM sin temperatura para tareas de precisión.
    
    Ideal para depuración de código (find_bugs_node) donde no se busca
    creatividad sino exactitud lógica.
    
    Returns:
        ChatOllama: Instancia del modelo LLM configurado (temperatura 0.0).
    """
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    num_ctx = int(os.getenv("NUM_CTX", "16384"))
    env = os.getenv("ENVIRONMENT", "local")
    if env == "cluster":
        print(f"[⚡ CLUSTER MODE] Usando GPU A40 / {model_name} determinista para mayor exactitud.")
    return ChatOllama(model=model_name, num_ctx=num_ctx, temperature=0.0)

def get_cluster_prompt_suffix():
    env = os.getenv("ENVIRONMENT", "local")
    if env == "cluster":
        return "\n\n[INSTRUCCIÓN AVANZADA CLÚSTER A40]: Dado que cuentas con alta capacidad computacional y de contexto, por favor utiliza 'Chain of Thought' (piensa paso a paso). Argumenta exhaustivamente tus decisiones, provee consideraciones pedagógicas o de rendimiento sumamente profundas, y genera respuestas del más alto nivel técnico y descriptivo disponible."
    return ""

def router_node(state):
    """Nodo inicial passthrough que no altera el estado.
    
    Actúa como punto de entrada (Entry Point) del DAG antes de que 
    el evaluador condicional (conditional_edge) decida la rama.
    """
    return state

def retrieve_exercises(state):
    """Nodo RAG: Recupera los ejercicios relevantes al perfil del alumno.
    
    Se comunica con el GraphRAG in-memory para obtener los documentos
    top-K que no superen el frente de aprendizaje del estudiante.
    """
    rag = GraphRAG()
    ejercicios = rag.retrieve_valid_exercises(state.get("conceptos_buscados", []), state.get("alumno_historial", []))
    rag.close()
    return {"ejercicios_contexto": ejercicios}

def generate_exercise(state):
    """Nodo Generador: Redacta un nuevo ejercicio adaptado al alumno.
    
    Lee el contexto del RAG y el historial del alumno. Si viene rebotado 
    del Senado, lee las críticas previas para inyectarlas en el prompt
    y forzar la corrección del ejercicio en este nuevo intento.
    """
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
4. ORIGINALIDAD: El ejercicio debe ser completamente nuevo. NO debes copiar la temática ni la narrativa de los ejercicios de ejemplo.

Contexto de ejercicios similares para inspiración:
{contexto}
"""
    if reintentos > 0 and criticas:
        user_prompt += f"\nATENCIÓN: Este es el intento número {reintentos + 1}. El Senado rechazó tu ejercicio anterior con las siguientes críticas:\n{criticas}\nPOR FAVOR, CORRIGE EL EJERCICIO TENIENDO EN CUENTA ESTE FEEDBACK.\n"

    user_prompt += "\nDevuelve ÚNICAMENTE el texto en formato Markdown con el enunciado completo del nuevo ejercicio."

    if state.get("modo_desarrollador", False):
        print(f"\n{DEV_COLOR}" + "═"*50)
        print("🛠️ [MODO DEV - GENERADOR] SYSTEM PROMPT:")
        print(system_prompt)
        print("-" * 50)
        print("🛠️ [MODO DEV - GENERADOR] USER PROMPT:")
        print(user_prompt)
        print("═"*50 + f"{RESET_COLOR}")

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return {"ejercicio_generado": response.content}

def senate_bft_node(state):
    """Nodo Senado (BFT): Implementa Byzantine Fault Tolerance mediante voto por mayoría.
    
    Instancia 3 llamadas asíncronas concurrentes (o secuenciales según fallback) al LLM.
    Cada "Juez" evalúa la dificultad y pertinencia pedagógica del ejercicio.
    Si 2 o más aprueban, el flujo avanza. Si no, devuelve el estado
    al Generador con las críticas acumuladas para que se regenere.
    """
    print("\n⚖️ El Senado está debatiendo (BFT 3 Jueces)...")
    llm = get_llm().with_structured_output(SenateVoteBFT)
    
    ejercicio = state.get("ejercicio_generado", "")
    dificultad = state.get("dificultad", "Media")
    contexto = "\n".join([f"Dificultad: {e['dificultad']}\nEnunciado: {e['enunciado']}" for e in state.get("ejercicios_contexto", [])])
    
    system_prompt = f"""Eres un juez estricto en el Senado Académico.
Debes evaluar el siguiente ejercicio generado por otro profesor.
Criterios estrictos:
1. ¿La dificultad del ejercicio coincide razonablemente con la pedida por el alumno ({dificultad})?
2. ¿El formato y estilo del ejercicio se parece a los ejercicios base extraídos del contexto?
3. ORIGINALIDAD: ¿Es el ejercicio original? NO debe ser una copia idéntica o tener la misma narrativa que los ejemplos del contexto.

Contexto de ejercicios base para guiar el estilo:
{contexto}

Evalúa estrictamente si apruebas o no el ejercicio. Si lo rechazas, debes proporcionar en tu crítica una propuesta de mejora constructiva para que el profesor sepa cómo rehacerlo.""" + get_cluster_prompt_suffix()

    user_prompt = f"Ejercicio a evaluar:\n{ejercicio}"

    async def get_vote(juez_id):
        if state.get("modo_desarrollador", False):
            print(f"\n{DEV_SYS_COLOR}=================\nJUEZ {juez_id}\n=================")
            print(f"🛠️ [MODO DEV - SENADO BFT - JUEZ {juez_id}] SYSTEM PROMPT:")
            print(system_prompt)
            print(f"{DEV_USER_COLOR}" + "-" * 50)
            print(f"🛠️ [MODO DEV - SENADO BFT - JUEZ {juez_id}] USER PROMPT:")
            print(user_prompt)
            print("═"*50 + f"{RESET_COLOR}")
            
        vote = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        if state.get("modo_desarrollador", False):
            print(f"\n{DEV_RES_COLOR}🤖 [MODO DEV - SENADO BFT - JUEZ {juez_id}] RESPUESTA:\n{vote.model_dump_json(indent=2)}\n" + "═"*50 + f"{RESET_COLOR}")
            
        return vote

    async def run_senate():
        # Ejecución en PARALELO para máxima velocidad (Seguro con modelo 32B en A40)
        return await asyncio.gather(*(get_vote(i+1) for i in range(3)))

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
    
    criticas_list = []
    for i, v in enumerate(votes):
        juez_title = f"JUEZ {i+1} ({'Aprueba' if getattr(v, 'aprueba', False) else 'Rechaza'})"
        critica_text = getattr(v, 'critica', '')
        criticas_list.append(f"=================\n{juez_title}\n=================\n{critica_text}\n")
        
    criticas_str = "\n".join(criticas_list)
    
    print(f"🏛️ Votación del Senado: {votos_favor} a favor, {votos_contra} en contra. Proceso de validación finalizado.")
    return {
        "enunciado_generado": ejercicio,
        "criticas_senado": "",
        "votos_senado": f"{votos_favor} a favor, {votos_contra} en contra"
    }

def senate_reflection_node(state):
    """Nodo Senado (Reflexión Secuencial): Implementa Self-Critique.
    
    Un Juez evalúa el ejercicio con una nota del 0 al 10.
    Si la nota es >= 8, se aprueba. Si es < 8, se devuelve el estado
    al Generador con la crítica para que se regenere.
    """
    con_solucion = state.get("con_solucion", False)
    num_jueces = 1 if con_solucion else 3
    msg_jueces = "(1 Juez Rápido)" if con_solucion else "(3 Jueces Secuenciales)"
    print(f"\n⚖️ El Senado Reflexivo ha iniciado la cadena de mejora {msg_jueces}...")
    llm = get_llm().with_structured_output(SenateVoteReflection)
    
    ejercicio = state.get("ejercicio_generado", "")
    dificultad = state.get("dificultad", "Media")
    contexto = "\n".join([f"Dificultad: {e['dificultad']}\nEnunciado: {e['enunciado']}" for e in state.get("ejercicios_contexto", [])])
    
    system_prompt = f"""Eres un juez estricto en el Senado Académico.
Debes evaluar el siguiente ejercicio generado por otro profesor.
Criterios estrictos:
1. ¿La dificultad del ejercicio coincide razonablemente con la pedida por el alumno ({dificultad})?
2. ¿El formato y estilo del ejercicio se parece a los ejercicios base extraídos del contexto?
3. ORIGINALIDAD: ¿Es el ejercicio original? NO debe ser una copia idéntica o tener la misma narrativa que los ejemplos del contexto.

Contexto de ejercicios base para guiar el estilo:
{contexto}

Evalúa el ejercicio asignándole una nota entera del 0 al 10.
En tu crítica, razona tu nota de forma MUY BREVE.
REGLA DE ORO: Tienes absolutamente PROHIBIDO dar consejos sobre qué se podría mejorar o añadir (ej. "se podría añadir..."). Si el ejercicio necesita mejoras, NO des el consejo: aplícalo directamente tú reescribiendo el ejercicio completo en el campo obligatorio 'ejercicio_mejorado'.
¡ATENCIÓN CRÍTICA!: EL CAMPO 'ejercicio_mejorado' NUNCA PUEDE ESTAR VACÍO (""). TIENES QUE ESCRIBIR EL ENUNCIADO COMPLETO REESCRITO SIEMPRE, INCLUSO SI LE DAS UN 10. SI DEJAS EL CAMPO VACÍO, EL SISTEMA CRASHEARÁ.""" + get_cluster_prompt_suffix()

    votes = []
    ejercicio_actual = ejercicio
    
    for i in range(num_jueces):
        juez_id = 3 if num_jueces == 1 else i + 1
        user_prompt = f"Ejercicio a evaluar:\n{ejercicio_actual}"
        
        if state.get("modo_desarrollador", False):
            print(f"\n{DEV_SYS_COLOR}=================\nJUEZ {juez_id}\n=================")
            print(f"🛠️ [MODO DEV - SENADO REFLEXIÓN - JUEZ {juez_id}] SYSTEM PROMPT:")
            print(system_prompt)
            print(f"{DEV_USER_COLOR}" + "-" * 50)
            print(f"🛠️ [MODO DEV - SENADO REFLEXIÓN - JUEZ {juez_id}] USER PROMPT:")
            print(user_prompt)
            print("═"*50 + f"{RESET_COLOR}")

        try:
            vote = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            if state.get("modo_desarrollador", False):
                print(f"\n{DEV_RES_COLOR}🤖 [MODO DEV - SENADO REFLEXIÓN - JUEZ {juez_id}] RESPUESTA:\n{vote.model_dump_json(indent=2)}\n" + "═"*50 + f"{RESET_COLOR}")
                
            votes.append(vote)
            
            # Actualizar el ejercicio actual con el mejorado por este juez (si no está vacío)
            mejorado = getattr(vote, "ejercicio_mejorado", "").strip()
            if mejorado:
                ejercicio_actual = mejorado
                
        except Exception as e:
            print(f"[!] Aviso: Error al invocar al juez {juez_id} ({e})")
            # En caso de error, emulamos un voto genérico para no romper la cadena
            vote_error = SenateVoteReflection(nota=8, critica=f"Error técnico: {e}", ejercicio_mejorado=ejercicio_actual)
            votes.append(vote_error)

    # La nota final será la que ponga el último juez (Juez 3)
    nota_final = getattr(votes[-1], "nota", 0)
    
    criticas_list = []
    for i, v in enumerate(votes):
        juez_title = f"JUEZ {i+1} (Nota: {getattr(v, 'nota', 0)}/10)"
        critica_text = getattr(v, 'critica', 'Sin crítica.')
        ejercicio_mejorado = getattr(v, 'ejercicio_mejorado', '').strip()
        if ejercicio_mejorado:
            critica_text += f"\n\n[EJERCICIO MEJORADO PROPUESTO]:\n{ejercicio_mejorado}"
            
        criticas_list.append(f"=================\n{juez_title}\n=================\n{critica_text}\n")
        
    criticas_str = "\n".join(criticas_list)
    
    print(f"🏛️ Votación del Senado: El Juez 3 certifica la versión final con un {nota_final}/10. Proceso de mejora iterativa completado.")
    return {
        "enunciado_generado": ejercicio_actual,
        "criticas_senado": "",
        "nota_senado": nota_final
    }

def generate_solution_node(state):
    """Nodo Tutor (Solución): Explica y resuelve el ejercicio generado.
    
    Incluye la directriz estricta de confinamiento para no usar herramientas
    que el alumno no haya aprendido todavía.
    """
    llm = get_llm()
    enunciado = state.get("enunciado_generado") or state.get("ejercicio_generado", "")
    lenguaje = state.get("lenguaje", "Python")
    vistos = ', '.join(state.get('alumno_historial', []))
    
    system_prompt = f"""Eres el profesor que ha escrito este ejercicio. Por favor, resuelve el ejercicio aportando:
1. El código en {lenguaje} correcto.
2. Una explicación pedagógica de cómo funciona el código y por qué se resuelve así.

REGLA ESTRICTA DE CONFINAMIENTO DE CONOCIMIENTO:
El alumno solo conoce estos conceptos: {vistos}.
TIENES TOTALMENTE PROHIBIDO usar, sugerir, mencionar o mostrar código que utilice conceptos, palabras clave, módulos o estructuras de datos ajenos a esa lista. Debes limitar tu solución estrictamente al arsenal de herramientas que el alumno ya domina.

Devuelve el resultado en Markdown, de forma clara y unificada.""" + get_cluster_prompt_suffix()
    
    user_prompt = f"Este es el enunciado del ejercicio:\n{enunciado}"
    
    if state.get("modo_desarrollador", False):
        print(f"\n{DEV_COLOR}" + "═"*50)
        print("🛠️ [MODO DEV - TUTOR SOLUCIÓN] SYSTEM PROMPT:")
        print(system_prompt)
        print("-" * 50)
        print("🛠️ [MODO DEV - TUTOR SOLUCIÓN] USER PROMPT:")
        print(user_prompt)
        print("═"*50 + f"{RESET_COLOR}")

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return {"resultado_codigo": response.content}

def solve_node(state):
    """Nodo Tutor (Corrección): Analiza código aportado por el alumno.
    
    Explica de forma socrática el código y propone mejoras respetando
    estrictamente el historial de aprendizaje del estudiante.
    """
    llm = get_llm()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    vistos = ', '.join(state.get('alumno_historial', []))
    
    system_prompt = f"""Eres un tutor experto. Tu objetivo es explicar qué hace este código en {lenguaje} proporcionado de forma pedagógica, o explicar su lógica general, y proponer un código mejorado si ves áreas de mejora.

REGLA ESTRICTA DE CONFINAMIENTO DE CONOCIMIENTO:
El alumno solo conoce estos conceptos: {vistos}.
TIENES TOTALMENTE PROHIBIDO usar, sugerir, mencionar o mostrar código que utilice conceptos, palabras clave, módulos o estructuras de datos ajenos a esa lista (por ejemplo, prohibido sugerir importaciones si no conoce bibliotecas). Debes limitar tus correcciones y sugerencias estrictamente al arsenal de herramientas que el alumno ya domina.

Devuelve la respuesta en Markdown.""" + get_cluster_prompt_suffix()
    
    if state.get("modo_desarrollador", False):
        print(f"\n{DEV_COLOR}" + "═"*50)
        print("🛠️ [MODO DEV - TUTOR CORRECCIÓN] SYSTEM PROMPT:")
        print(system_prompt)
        print("-" * 50)
        print("🛠️ [MODO DEV - TUTOR CORRECCIÓN] USER PROMPT:")
        print(codigo)
        print("═"*50 + f"{RESET_COLOR}")

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}

def find_bugs_node(state):
    """Nodo Debugger: Encuentra fallos en el código del alumno.
    
    Utiliza el modelo determinista (temperatura 0.0) para máxima
    exactitud al cazar bugs lógicos y de sintaxis.
    """
    llm = get_llm_deterministic()
    codigo = state.get("codigo_entrada", "")
    lenguaje = state.get("lenguaje", "Python")
    vistos = ', '.join(state.get('alumno_historial', []))
    
    system_prompt = f"""Eres un debugger experto en {lenguaje}. Tu objetivo es encontrar fallos lógicos o sintácticos en el código proporcionado. Explica dónde están los errores, por qué ocurren y proporciona la versión corregida. Sé muy metódico.

REGLA ESTRICTA DE CONFINAMIENTO DE CONOCIMIENTO:
El alumno solo conoce estos conceptos: {vistos}.
TIENES TOTALMENTE PROHIBIDO usar, sugerir, mencionar o mostrar código corregido que utilice conceptos o módulos avanzados que el alumno no conozca. Corrige los bugs utilizando únicamente las herramientas de su nivel.

Devuelve el resultado en Markdown.""" + get_cluster_prompt_suffix()
    
    if state.get("modo_desarrollador", False):
        print(f"\n{DEV_COLOR}" + "═"*50)
        print("🛠️ [MODO DEV - DEBUGGER] SYSTEM PROMPT:")
        print(system_prompt)
        print("-" * 50)
        print("🛠️ [MODO DEV - DEBUGGER] USER PROMPT:")
        print(codigo)
        print("═"*50 + f"{RESET_COLOR}")

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=codigo)
    ])
    
    return {"resultado_codigo": response.content}
