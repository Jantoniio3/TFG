import os
import sys

# Agregar src a los paths por si se invoca desde la raíz
sys.path.append(os.path.dirname(__file__))

from src.agents.graph import build_graph
import networkx as nx
from src.ontology.grafo import concepto_dominio, construir_grafo

def get_multiline_input(prompt):
    print(prompt)
    print("(Pega tu código. Escribe 'FIN' en una nueva línea y presiona Enter para finalizar)")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'FIN':
            break
        lines.append(line)
    return "\n".join(lines)

def main():
    print("-" * 50)
    print("🧠 TUTOR INTELIGENTE - MULTI-AGENTE (DEMO CONSOLA) 🧠")
    print("-" * 50)
    
    app = build_graph()
    
    conceptos_db = list(concepto_dominio().keys())
        
    historial_alumno = []
    lenguaje_sesion = "Python"
    
    # Bucle infinito del Menú
    while True:
        print("\n" + "=" * 40)
        print("💡 MENÚ PRINCIPAL")
        print("========================================")
        print("1. Generar Ejercicio")
        print("2. Resolver Código")
        print("3. Buscar Bugs")
        print("4. Salir")
        
        opcion = input("\n📝 Elige una opción: ").strip()
        
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
            if conceptos_db:
                print("📚 CONCEPTOS DISPONIBLES EN LA ONTOLOGÍA:")
                print(', '.join(conceptos_db))
            print("-" * 50)
            print("\nIndica los conceptos que YA HAS ESTUDIADO (tu perfil). Separa por comas.")
            vistos_input = input("Conceptos vistos [Dejar en blanco para usar perfil DEMO]: ")
            if vistos_input.strip():
                conceptos_base = [c.strip() for c in vistos_input.split(",") if c.strip()]
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
            
            print(f"✅ Perfil configurado y guardado. Conoces {len(historial_alumno)} conceptos.")
            
            # Pedir lenguaje una sola vez
            req_lenguaje = input("¿En qué lenguaje de programación quieres trabajar? [Por defecto: Python]: ").strip()
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
            "resultado_codigo": ""
        }
            
        if opcion == "1":
            print(f"\n📋 Tu Perfil ({len(historial_alumno)} conceptos).")
            # Dejamos la opción de presionar "Enter" si quieren repasar todo su conocimiento o usar por defecto
            entrada = input("¿Qué conceptos te gustaría practicar? (Ej: Variable) [Rellena u oprime Enter para aleatorio]: ")
            if entrada.strip():
                buscados = [c.strip() for c in entrada.split(",") if c.strip()]
            else:
                # Si no pone nada, agarramos 1 o 2 conceptos de su historial
                import random
                buscados = random.sample(historial_alumno, min(2, len(historial_alumno)))
                print(f"🎲 Seleccionados aleatoriamente: {', '.join(buscados)}")
            
            dificultad = input("Dificultad (Fácil/Media/Difícil) [Por defecto: Media]: ").strip()
            dificultad = dificultad if dificultad else "Media"
            
            con_solucion = input("¿Generar también la solución explicada? (s/n): ").strip().lower() == "s"
            
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
            final_state = app.invoke(initial_state)
            
            print("\n" + "*" * 50)
            print("🎯 RESULTADO 🎯")
            print("*" * 50)
            
            if final_state.get("tarea") == "generar":
                print(f"\n[ENUNCIADO]\n{final_state.get('enunciado_generado')}")
                if final_state.get("con_solucion"):
                    print(f"\n[SOLUCIÓN Y EXPLICACIÓN]\n{final_state.get('resultado_codigo')}")
            else:
                print(f"\n[RESPUESTA DEL TUTOR]\n{final_state.get('resultado_codigo')}")
        except Exception as e:
            print(f"\n[ERROR] Ocurrió un problema ejecutando el grafo: {e}")

if __name__ == "__main__":
    main()
