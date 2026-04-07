import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langgraph.graph import StateGraph, END
from src.agents.state import TutorState
from src.agents.nodes import router_node, retrieve_exercises, generate_exercise, generate_solution_node, solve_node, find_bugs_node

def route_task(state):
    return state.get("tarea", "generar")

def route_solution(state):
    if state.get("con_solucion", False):
        return "generate_solution_node"
    return "end"

def build_graph():
    workflow = StateGraph(TutorState)
    
    # Agregar nodos
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retrieve_exercises)
    workflow.add_node("generator", generate_exercise)
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
    workflow.add_conditional_edges("generator", route_solution, {
        "generate_solution_node": "generate_solution_node",
        "end": END
    })
    workflow.add_edge("generate_solution_node", END)
    
    # Otras ramas terminan directo
    workflow.add_edge("solve_node", END)
    workflow.add_edge("find_bugs_node", END)
    
    return workflow.compile()
