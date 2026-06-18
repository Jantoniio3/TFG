"""Laboratorio de Stress Testing (Consistencia y Latencia).

Ejecuta el pipeline de generación de ejercicios múltiples veces bajo las
mismas condiciones para evaluar la varianza determinística del LLM,
la tasa de aprobación del Senado y la latencia promedio del sistema.
"""

import os
import sys
import io
import time
import csv
import asyncio
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Asegurar que el path alcanza la raíz
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.graph import build_graph

async def run_stress_test(N: int = 10):
    """Ejecuta el test de estrés N veces de forma secuencial."""
    
    print("=" * 60)
    print(f"INICIANDO STRESS TESTING (N={N})")
    print("=" * 60)
    print("Midiendo latencia, varianza del Senado y tasa de reintentos...\n")
    
    # Compilar el grafo
    app = build_graph()
    
    # Permitir sobreescribir el modelo por argumento CLI (ej: python consistency_test.py 10 llama3.1:8b)
    load_dotenv()
    if len(sys.argv) > 2:
        modelo = sys.argv[2]
        os.environ["OLLAMA_MODEL"] = modelo
    else:
        modelo = os.getenv("OLLAMA_MODEL", "Desconocido")
        
    if len(sys.argv) > 3:
        num_ctx = sys.argv[3]
        os.environ["NUM_CTX"] = num_ctx
    else:
        num_ctx = os.getenv("NUM_CTX", "16384")
    
    # Archivo de salida
    csv_filename = "stress_test_results.csv"
    headers = [
        "Iteracion", 
        "Modelo", 
        "Ventana_Contexto",
        "Tipo_Senado",
        "Tiempo_Total_Generacion_Min", 
        "Puntuacion_Senado", 
        "Reintentos", 
        "Resultado_Final"
    ]
    
    resultados = []
    
    # Verificar si el archivo ya existe para no repetir las cabeceras
    file_exists = os.path.isfile(csv_filename) and os.path.getsize(csv_filename) > 0
    
    # Abrir el CSV en modo append ('a') para añadir al final sin machacar
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Escribir cabeceras solo si el archivo es nuevo
        if not file_exists:
            writer.writerow(headers)
        
        for i in range(1, N + 1):
            print(f"[{i}/{N}] Generando ejercicio de alta dificultad (Recursividad)...")
            
            # Estado base fijo y complejo
            initial_state = {
                "tarea": "generar",
                "con_solucion": False,
                "lenguaje": "Python",
                "codigo_entrada": "",
                "resultado_codigo": "",
                "alumno_historial": ["Variable", "Tipo de dato", "Función", "Sentencia condicional", "Bucle for", "Bucle while", "Recursividad"],
                "conceptos_buscados": ["Recursividad"],
                "dificultad": "Difícil",
                "ejercicios_contexto": [],
                "enunciado_generado": "",
                "codigo_solucion": "",
                "explicacion": "",
                "reintentos": 0,
                "ejercicio_generado": "",
                "criticas_senado": "",
                "votos_senado": "",
                "nota_senado": 0,
                "usar_senado": True,
                "tipo_senado": "reflexion" # Usamos el senado en línea (reflexión)
            }
            
            start_time = time.perf_counter()
            
            # Ejecutar el grafo de LangGraph de forma asíncrona mostrando progreso
            async for s in app.astream(initial_state, config={"recursion_limit": 20}):
                for node_name, node_state in s.items():
                    if node_name == "retriever":
                        print("   [25%] 🔍 RAG: Recuperando contexto de la base de datos...")
                    elif node_name == "generator":
                        print("   [50%] ✍️ LLM: Redactando borrador base del ejercicio...")
                    elif node_name == "senate_bft_node" or node_name == "senate_reflection_node":
                        pass # El senado ya imprime sus votaciones internamente
                    
                    # Acumular el estado para extraer métricas al final
                    initial_state.update(node_state)
            
            final_state = initial_state
            
            end_time = time.perf_counter()
            tiempo_total_min = round((end_time - start_time) / 60.0, 2)
            
            # Extracción de métricas
            reintentos = final_state.get("reintentos", 0)
            tipo_evaluacion = initial_state.get("tipo_senado", "bft")
            
            puntuacion = "0"
            if tipo_evaluacion == "reflexion":
                puntuacion = f"{final_state.get('nota_senado', 0)}/10"
            elif tipo_evaluacion == "bft":
                puntuacion = final_state.get("votos_senado", "0 a favor")
            
            # Determinar si al final de todo el proceso el ejercicio se aprobó
            if not final_state.get("criticas_senado"):
                resultado = "Aprobado"
            else:
                resultado = "Fallido (Límite de reintentos)"
                
            print(f"   Tiempo: {tiempo_total_min}min | Puntuación Final: {puntuacion} | Reintentos: {reintentos} | Resultado: {resultado}")
            
            row = [i, modelo, num_ctx, tipo_evaluacion, tiempo_total_min, puntuacion, reintentos, resultado]
            writer.writerow(row)
            f.flush() # Guardar a disco inmediatamente por si se cancela a medias
            
    print("\n" + "=" * 60)
    print(f"Stress Testing completado. Resultados guardados en: {csv_filename}")
    print("=" * 60)

if __name__ == "__main__":
    # Uso: python consistency_test.py [N_ITERACIONES] [MODELO_OPCIONAL] [NUM_CTX_OPCIONAL]
    # Ej: python consistency_test.py 5 qwen2.5-coder:7b 8192
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(run_stress_test(N))
