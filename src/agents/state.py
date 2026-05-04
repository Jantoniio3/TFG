"""Define el estado de la máquina de estados de LangGraph para el Tutor Inteligente.

Este módulo contiene la definición del estado global que transita
por los distintos nodos de LangGraph (Generador, Senado, Debugger).
"""

from typing import TypedDict, List, Literal, Optional

class TutorState(TypedDict):
    """Representa el estado del agente en cada paso de ejecución.
    
    Attributes:
        tarea (Literal): Tipo de tarea a ejecutar ("generar", "resolver", "debug").
        con_solucion (bool): Indica si se debe generar también la solución al ejercicio.
        lenguaje (str): Lenguaje de programación objetivo (ej. "Python").
        codigo_entrada (str): Código proporcionado por el alumno para corrección o explicación.
        resultado_codigo (str): Respuesta final en Markdown generada por el LLM.
        alumno_historial (List[str]): Lista de conceptos que el alumno domina.
        conceptos_buscados (List[str]): Conceptos específicos sobre los que tratará el ejercicio.
        dificultad (str): Nivel de dificultad ("Fácil", "Media", "Difícil").
        ejercicios_contexto (List[dict]): Ejercicios extraídos del Graph RAG como base.
        enunciado_generado (str): El enunciado final aprobado por el Senado.
        codigo_solucion (str): El código de solución generado (actualmente unificado en resultado_codigo).
        explicacion (str): Explicación pedagógica de la solución.
        reintentos (int): Número de veces que el Senado ha rechazado el ejercicio.
        ejercicio_generado (str): El borrador actual del ejercicio (en evaluación).
        criticas_senado (str): Histórico de críticas de los jueces para guiar la regeneración.
    """
    tarea: Literal["generar", "resolver", "debug"]
    con_solucion: bool
    lenguaje: str
    codigo_entrada: str
    resultado_codigo: str
    alumno_historial: List[str]
    conceptos_buscados: List[str]
    dificultad: str
    ejercicios_contexto: List[dict]
    enunciado_generado: str
    codigo_solucion: str
    explicacion: str
    reintentos: int
    ejercicio_generado: str
    criticas_senado: str
    votos_senado: str
