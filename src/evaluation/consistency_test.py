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
    
    # Archivo de salida
    csv_filename = "stress_test_results.csv"
    headers = [
        "Iteracion", 
        "Modelo", 
        "Tiempo_Total_Generacion_Seg", 
        "Votos_Senado", 
        "Reintentos", 
        "Resultado_Final"
    ]
    
    resultados = []
    
    # Abrir el CSV en modo escritura (sobrescribe si existe)
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
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
                "votos_senado": ""
            }
            
            start_time = time.perf_counter()
            
            # Ejecutar el grafo de LangGraph de forma asíncrona
            final_state = await app.ainvoke(initial_state, config={"recursion_limit": 20})
            
            end_time = time.perf_counter()
            tiempo_total = round(end_time - start_time, 2)
            
            # Extracción de métricas
            reintentos = final_state.get("reintentos", 0)
            votos = final_state.get("votos_senado", "Desconocido")
            
            # Determinar si al final de todo el proceso el ejercicio se aprobó
            # (Si no hay críticas en el estado final, es que el Senado lo aprobó)
            if not final_state.get("criticas_senado"):
                resultado = "Aprobado"
            else:
                resultado = "Fallido (Límite de reintentos)"
                
            print(f"   Tiempo: {tiempo_total}s | Votos: {votos} | Reintentos: {reintentos} | Resultado: {resultado}")
            
            row = [i, modelo, tiempo_total, votos, reintentos, resultado]
            writer.writerow(row)
            f.flush() # Guardar a disco inmediatamente por si se cancela a medias
            
    print("\n" + "=" * 60)
    print(f"Stress Testing completado. Resultados guardados en: {csv_filename}")
    print("=" * 60)

if __name__ == "__main__":
    # Uso: python consistency_test.py [N_ITERACIONES] [MODELO_OPCIONAL]
    # Ej: python consistency_test.py 5 qwen2.5-coder:7b
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(run_stress_test(N))
