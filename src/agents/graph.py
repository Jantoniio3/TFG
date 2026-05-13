"""Orquestador del flujo de agentes usando LangGraph.

Este módulo define la topología del Grafo Acíclico Dirigido (DAG) que controla
las interacciones entre el RAG, el LLM Generador, el Senado y el Debugger.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, END
from src.agents.state import TutorState
from src.agents.nodes import router_node, retrieve_exercises, generate_exercise, senate_bft_node, senate_reflection_node, generate_solution_node, solve_node, find_bugs_node

def route_task(state: TutorState) -> str:
    """Enruta el flujo inicial hacia la rama correspondiente según la tarea.
    
    Args:
        state: El estado actual del tutor.
        
    Returns:
        str: El nombre del siguiente nodo ("retriever", "solve_node", "find_bugs_node").
    """
    return state.get("tarea", "generar")

def route_post_generator(state: TutorState) -> str:
    """Decide si enviar el ejercicio al Senado o saltarse la evaluación.
    
    Args:
        state: El estado actual del tutor.
        
    Returns:
        str: El siguiente nodo ("senate_evaluation_node", "generate_solution_node", "end").
    """
    tipo_senado = state.get("tipo_senado", "reflexion")
    
    if tipo_senado == "bft":
        return "senate_bft_node"
    elif tipo_senado == "reflexion":
        return "senate_reflection_node"
    else: # "ninguno"
        if state.get("con_solucion", False):
            return "generate_solution_node"
        return "end"

def route_senate(state: TutorState) -> str:
    """Decide el siguiente paso tras la votación del Senado (Tolerancia a fallos).
    
    Si el Senado rechaza el ejercicio, enruta de vuelta al Generador para reintentar.
    Si se supera el límite de reintentos (3), finaliza el grafo para evitar bucles infinitos.
    Si el Senado lo aprueba, enruta a la solución o finaliza.
    
    Args:
        state: El estado actual del tutor.
        
    Returns:
        str: El siguiente nodo en el flujo ("generator", "generate_solution_node", "end").
    """
    if state.get("criticas_senado"):
        if state.get("reintentos", 0) < 3:
            return "generator"
        else:
            print("\n❌ Límite de reintentos alcanzado. El Senado no pudo aprobar el ejercicio. Terminando...")
            return "end"
    else:
        if state.get("con_solucion", False):
            return "generate_solution_node"
        return "end"

def build_graph():
    """Construye y compila la máquina de estados (Grafo) de LangGraph.
    
    Returns:
        CompiledStateGraph: El grafo compilado listo para ser invocado (.invoke() o .stream()).
    """
    workflow = StateGraph(TutorState)
    
    # Agregar nodos
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retrieve_exercises)
    workflow.add_node("generator", generate_exercise)
    workflow.add_node("senate_bft_node", senate_bft_node)
    workflow.add_node("senate_reflection_node", senate_reflection_node)
    workflow.add_node("generate_solution_node", generate_solution_node)
    workflow.add_node("solve_node", solve_node)
    workflow.add_node("find_bugs_node", find_bugs_node)
    
    # Set the Entry Point
    workflow.set_entry_point("router")
    
    # Router conditional edges
    workflow.add_conditional_edges("router", route_task, {
        "generar": "retriever",
        "resolver": "solve_node",
        "debug": "find_bugs_node"
    })
    
    # Generar rama
    workflow.add_edge("retriever", "generator")
    workflow.add_conditional_edges("generator", route_post_generator, {
        "senate_bft_node": "senate_bft_node",
        "senate_reflection_node": "senate_reflection_node",
        "generate_solution_node": "generate_solution_node",
        "end": END
    })
    
    # Ambos senados usan la misma lógica de ruteo post-evaluación
    workflow.add_conditional_edges("senate_bft_node", route_senate, {
        "generator": "generator",
        "generate_solution_node": "generate_solution_node",
        "end": END
    })
    workflow.add_conditional_edges("senate_reflection_node", route_senate, {
        "generator": "generator",
        "generate_solution_node": "generate_solution_node",
        "end": END
    })
    workflow.add_edge("generate_solution_node", END)
    
    # Otras ramas terminan directo
    workflow.add_edge("solve_node", END)
    workflow.add_edge("find_bugs_node", END)
    
    return workflow.compile()
