from typing import TypedDict, List, Literal, Optional

class TutorState(TypedDict):
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
