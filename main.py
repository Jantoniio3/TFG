"""Punto de entrada principal del Tutor Inteligente Multi-Agente.

Este script inicializa la Interfaz de Línea de Comandos (CLI),
configura el estado inicial del estudiante leyendo la ontología de conceptos,
y lanza la ejecución en modo streaming del DAG de LangGraph.
"""

import os
import sys
import unicodedata
import threading
import itertools
import time
from dotenv import load_dotenv

# Colores ANSI para diferenciar texto
USER_COLOR = "\033[96m"  # Cyan para lo que escribe el usuario
TUTOR_COLOR = "\033[92m" # Verde para las respuestas finales del tutor
SYS_COLOR = "\033[93m"   # Amarillo para los prompts del sistema
RESET_COLOR = "\033[0m"  # Reset

# Agregar src a los paths por si se invoca desde la raíz
sys.path.append(os.path.dirname(__file__))

def ask_user(prompt_text: str) -> str:
    """Imprime el prompt en amarillo, lee el input en cyan y resetea el color."""
    val = input(f"{SYS_COLOR}{prompt_text}{USER_COLOR}")
    print(RESET_COLOR, end="")
    return val

class Spinner:
    """Muestra un reloj de arena dinámico (spinner) en la consola usando un hilo en segundo plano."""
    def __init__(self, message="La IA está pensando..."):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.message = message
        self.busy = False
        self.thread = None

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
            
    def start(self):
        self.busy = True
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if not self.busy:
            return
        self.busy = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r\033[K') # Limpiar la línea
        sys.stdout.flush()

from src.agents.graph import build_graph
import networkx as nx
from src.ontology.grafo import concepto_dominio, construir_grafo, CONCEPTOS

def normalize_text(text: str) -> str:
    """Normaliza un texto eliminando tildes, espacios extra y pasándolo a minúsculas.
    
    Args:
        text (str): El texto introducido por el usuario.
        
    Returns:
        str: El texto normalizado (ej. "Función  " -> "funcion").
    """
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8").lower().strip()

def get_multiline_input(prompt: str) -> str:
    """Captura código multilínea desde la terminal hasta que el usuario escriba 'FIN'.
    
    Args:
        prompt (str): El mensaje a mostrar antes de pedir la entrada.
        
    Returns:
        str: El bloque de código completo como un único string.
    """
    print(f"{SYS_COLOR}{prompt}{RESET_COLOR}")
    print(f"{SYS_COLOR}(Pega tu código. Escribe 'FIN' en una nueva línea y presiona Enter para finalizar){RESET_COLOR}")
    lines = []
    while True:
        line = ask_user("")
        if line.strip().upper() == 'FIN':
            break
        lines.append(line)
    return "\n".join(lines)

def main():
    """Ejecuta el bucle principal de la aplicación CLI.
    
    Inicializa el grafo, pide la configuración del perfil del alumno (solo la primera vez),
    y orquesta las opciones de generar ejercicios, explicar código o buscar bugs,
    invocando el modelo de LangGraph en modo stream para mostrar el progreso.
    """
    print("-" * 50)
    print("🧠 TUTOR INTELIGENTE - MULTI-AGENTE (DEMO CONSOLA) 🧠")
    print("-" * 50)
    
    app = build_graph()
    
    conceptos_db = list(concepto_dominio().keys())
    conceptos_normalizados = {normalize_text(c): c for c in conceptos_db}
        
    historial_alumno = []
    conceptos_maximos = []
    lenguaje_sesion = "Python"
    
    load_dotenv()
    dev_mode_env = os.getenv("DEVELOPER_MODE", "False").strip().lower()
    modo_desarrollador = dev_mode_env in ("true", "1", "yes", "s")
    if modo_desarrollador:
        print("🛠️ MODO DESARROLLADOR ACTIVADO (desde .env). Prepárate para ver mucho texto en consola.")
        
    usar_senado = True
    tipo_senado = "bft"
    
    # Bucle infinito del Menú
    while True:
        print("\n" + "=" * 40)
        print("💡 MENÚ PRINCIPAL")
        print("========================================")
        print("1. Generar Ejercicio")
        print("2. Resolver Código")
        print("3. Buscar Bugs")
        print("4. Salir")
        
        opcion = ask_user("\n📝 Elige una opción: ").strip()
        
        if opcion == "4":
            print("¡Hasta pronto!")
            break
            
        if opcion not in ["1", "2", "3"]:
            print("Opción inválida.")
            continue
            
        # Pedir el perfil de conocimiento SOLO UNA VEZ en la sesión
        if not historial_alumno and opcion in ["1", "2"]:
            print("\n" + "-" * 50)
            print("👤 CONFIGURACIÓN DEL PERFIL DEL ALUMNO")
            if CONCEPTOS:
                print("📚 CONCEPTOS DISPONIBLES EN LA ONTOLOGÍA:")
                for dominio, lista_conceptos in CONCEPTOS.items():
                    print(f"\n   🔹 {dominio.upper()}:")
                    # Separar por comas y ajustar ancho
                    conceptos_format = ', '.join(lista_conceptos)
                    print(f"      {conceptos_format}")
            print("-" * 50)
            print("\nIndica los conceptos que YA HAS ESTUDIADO (tu perfil). Separa por comas.")
            vistos_input = ask_user("Conceptos vistos [Dejar en blanco para usar perfil DEMO]: ")
            if vistos_input.strip():
                conceptos_base_raw = [c.strip() for c in vistos_input.split(",") if c.strip()]
                conceptos_base = []
                for c in conceptos_base_raw:
                    norm_c = normalize_text(c)
                    if norm_c in conceptos_normalizados:
                        conceptos_base.append(conceptos_normalizados[norm_c])
                    else:
                        print(f"⚠️ El concepto '{c}' no existe en la ontología y será ignorado.")
                        
                conceptos_maximos = conceptos_base.copy()
                        
                print("🧠 Infiriendo dependencias previas desde el Grafo de Conocimiento In-Memory...")
                G_req = construir_grafo(["REQUIERE_PREVIO"])
                prerequisitos = set()
                for c in conceptos_base:
                    if c in G_req.nodes:
                        # Ancestors are nodes that have a path TO 'c' in the Directed Graph
                        # Since REQUIERE_PREVIO means (A) -REQUIERE_PREVIO-> (B) -> (A depends on B)
                        # Wait! In grafo.py:
                        # SEMÁNTICA: ("Origen", "Destino", "REQUIERE_PREVIO")
                        # "Para aprender 'origen' hay que dominar 'destino' antes."
                        # Which means Origen -> Destino.
                        # So Destino is the prerequisite!
                        # We need nodes reachable FROM 'c' downstream (successors and descendants).
                        prerequisitos.update(nx.descendants(G_req, c))
                
                historial_alumno = list(set(conceptos_base).union(prerequisitos))
                if prerequisitos:
                    print(f"   (Se han inferido automáticamente {len(historial_alumno) - len(conceptos_base)} conceptos previos subyacentes)")
            else:
                print("Usando perfil demo predefinido...")
                mock = ["Algoritmo", "Programa", "Variable", "Función", "Operador"]
                historial_alumno = [c for c in mock if c in conceptos_db] if conceptos_db else mock
                conceptos_maximos = ["Función", "Operador"]
            
            print(f"✅ Perfil configurado y guardado. Conoces {len(historial_alumno)} conceptos.")
            
            # Pedir lenguaje una sola vez
            req_lenguaje = ask_user("¿En qué lenguaje de programación quieres trabajar? [Por defecto: Python]: ").strip()
            lenguaje_sesion = req_lenguaje if req_lenguaje else "Python"
            print(f"✅ Establecido el lenguaje a {lenguaje_sesion} para esta sesión.")
            
        initial_state = {
            "alumno_historial": historial_alumno,
            "conceptos_buscados": [],
            "dificultad": "Media",
            "tarea": "generar",
            "con_solucion": False,
            "lenguaje": lenguaje_sesion,
            "codigo_entrada": "",
            "resultado_codigo": "",
            "modo_desarrollador": modo_desarrollador,
            "usar_senado": usar_senado,
            "tipo_senado": tipo_senado
        }
            
        if opcion == "1":
            print(f"\n📋 Tu Perfil ({len(historial_alumno)} conceptos).")
            # Dejamos la opción de presionar "Enter" si quieren repasar todo su conocimiento o usar por defecto
            entrada = ask_user("¿Qué conceptos te gustaría practicar? (Ej: Variable) [Rellena u oprime Enter para usar tu nivel máximo]: ")
            if entrada.strip():
                buscados_raw = [c.strip() for c in entrada.split(",") if c.strip()]
                buscados = []
                for c in buscados_raw:
                    norm_c = normalize_text(c)
                    if norm_c in conceptos_normalizados:
                        buscados.append(conceptos_normalizados[norm_c])
                    else:
                        print(f"⚠️ El concepto '{c}' no existe en la ontología y será ignorado.")
            else:
                # Si no pone nada, agarramos los conceptos máximos que introdujo en su perfil
                buscados = conceptos_maximos if conceptos_maximos else historial_alumno[:2]
                print(f"🎯 Seleccionados automáticamente (tu nivel máximo): {', '.join(buscados)}")
            
            dificultad = ask_user("Dificultad (Fácil/Media/Difícil) [Por defecto: Media]: ").strip()
            dificultad = dificultad if dificultad else "Media"
            
            con_solucion = ask_user("¿Generar también la solución explicada? (s/n): ").strip().lower() == "s"
            
            # Forzamos el uso del senado reflexivo en línea
            initial_state["tipo_senado"] = "reflexion"
            initial_state["usar_senado"] = True
            print("🧠 SENADO REFLEXIVO (EN LÍNEA) ACTIVADO.")
            
            initial_state["tarea"] = "generar"
            initial_state["conceptos_buscados"] = buscados
            initial_state["dificultad"] = dificultad
            initial_state["con_solucion"] = con_solucion
            
            print("\n⚙️ Lanzando grafo: Graph RAG + Generando Ejercicio...")
            
        elif opcion == "2":
            codigo = get_multiline_input("\nPegue el código que desea que el tutor le explique y resuelva:")
            if not codigo.strip():
                print("Operación cancelada.")
                continue
            initial_state["tarea"] = "resolver"
            initial_state["codigo_entrada"] = codigo
            print("\n⚙️ Lanzando grafo: Explicando Código con LLM...")
            
        elif opcion == "3":
            codigo = get_multiline_input("\nPegue el código que desea depurar:")
            if not codigo.strip():
                print("Operación cancelada.")
                continue
            initial_state["tarea"] = "debug"
            initial_state["codigo_entrada"] = codigo
            print("\n⚙️ Lanzando grafo: Buscando Bugs con LLM Determinista...")
            
        try:
            spinner = Spinner("⏳ La IA está razonando...")
            if not modo_desarrollador:
                spinner.start()
            
            # Usamos stream en vez de invoke para poder mostrar el progreso paso a paso
            for s in app.stream(initial_state, config={"recursion_limit": 20}):
                # Detener el spinner un momento para que los prints de los nodos no se solapen
                if not modo_desarrollador:
                    spinner.stop()
                
                for node_name, node_state in s.items():
                    if node_name == "retriever":
                        print("   [25%] 🔍 RAG: Evaluando tu nivel y recuperando temario...")
                    elif node_name == "generator":
                        pass
                    elif node_name == "senate_evaluation_node":
                        pass # El senado ya imprime sus votaciones internamente en nodes.py
                    elif node_name == "generate_solution_node":
                        print("   [90%] 💡 LLM: Generando la solución final explicada...")
                    elif node_name == "solve_node":
                        print("   [80%] 🧠 LLM: Analizando la lógica de tu código...")
                    elif node_name == "find_bugs_node":
                        print("   [80%] 🐛 Debugger: Ejecutando rastreo de código y vulnerabilidades...")
                    
                    # Guardamos el estado acumulativo
                    initial_state.update(node_state)
                
                # Reanudar el spinner hasta que se emita el siguiente estado
                if not modo_desarrollador:
                    spinner.start()
            
            if not modo_desarrollador:
                spinner.stop()
            final_state = initial_state
            
            print("\n" + "*" * 50)
            print("🎯 RESULTADO 🎯")
            print("*" * 50)
            
            if final_state.get("tarea") == "generar":
                ejercicio_final = final_state.get('enunciado_generado') or final_state.get('ejercicio_generado', '')
                print(f"\n{TUTOR_COLOR}[ENUNCIADO]\n{ejercicio_final}{RESET_COLOR}")
                if final_state.get("con_solucion"):
                    print(f"\n{TUTOR_COLOR}[SOLUCIÓN Y EXPLICACIÓN]\n{final_state.get('resultado_codigo')}{RESET_COLOR}")
                
                # Guardar en archivo
                try:
                    with open("exercice.md", "w", encoding="utf-8") as f:
                        f.write(f"# Ejercicio Generado\n\n## Enunciado\n{ejercicio_final}\n")
                        if final_state.get("con_solucion"):
                            f.write(f"\n## Solución y Explicación\n{final_state.get('resultado_codigo')}\n")
                    print("\n💾 Ejercicio guardado exitosamente en 'exercice.md'.")
                except Exception as e:
                    print(f"\n[ERROR] No se pudo guardar el archivo: {e}")
            else:
                print(f"\n{TUTOR_COLOR}[RESPUESTA DEL TUTOR]\n{final_state.get('resultado_codigo')}{RESET_COLOR}")
                # Guardar en archivo
                try:
                    with open("tutor_response.md", "w", encoding="utf-8") as f:
                        tarea_nombre = "Resolución de Código" if final_state.get("tarea") == "resolver" else "Análisis de Bugs"
                        f.write(f"# {tarea_nombre}\n\n")
                        f.write(f"## Código Proporcionado\n```python\n{final_state.get('codigo_entrada', '')}\n```\n\n")
                        f.write(f"## Análisis del Tutor Inteligente\n{final_state.get('resultado_codigo')}\n")
                    print("\n💾 Respuesta del tutor guardada exitosamente en 'tutor_response.md'.")
                except Exception as e:
                    print(f"\n[ERROR] No se pudo guardar el archivo: {e}")
        except Exception as e:
            print(f"\n[ERROR] Ocurrió un problema ejecutando el grafo: {e}")

if __name__ == "__main__":
    main()
