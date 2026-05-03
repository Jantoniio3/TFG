import sys
import os
import time
import asyncio
import csv
from dotenv import load_dotenv

# Asegurar que el path alcance 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.graph import build_graph

load_dotenv()

# Configuración del Laboratorio
MODELOS_A_TESTEAR = [
    "llama3.1:8b", 
    "qwen2.5-coder:7b", 
    "gemma2:9b", 
    "mistral:7b", 
    "phi3.5"
]

# Golden Dataset Mock (Casos controlados para aislar el rendimiento del LLM)
GOLDEN_DATASET = [
    {
        "desc": "Bucle For Simple",
        "tarea": "generar",
        "conceptos": ["Bucle For"],
        "dificultad": "Fácil",
        "historial": ["Variable", "Print", "Enteros"]
    },
    {
        "desc": "Función Recursiva",
        "tarea": "generar",
        "conceptos": ["Función", "Recursividad"],
        "dificultad": "Media",
        "historial": ["Variable", "Condicional", "Bucle For", "Bucle While"]
    },
    {
        "desc": "Estructuras Avanzadas",
        "tarea": "generar",
        "conceptos": ["Diccionario", "List Comprehension"],
        "dificultad": "Difícil",
        "historial": ["Variable", "Bucle For", "Listas", "Funciones"]
    }
]

async def ejecutar_benchmark():
    print("=" * 60)
    print("🧪 LABORATORIO DE BENCHMARKING MULTI-AGENTE (CLÚSTER)")
    print("=" * 60)
    print("INFO: Se probará la latencia y consenso de Byzantine Fault Tolerance.")
    print("Asegúrate de haber descargado los modelos (ollama pull <modelo>).")
    print("Iniciando evaluación...\n")
    
    app = build_graph()
    resultados = []
    
    # Forzamos entorno cluster por si acaso (para activar sufijos avanzados del prompt)
    os.environ["ENVIRONMENT"] = "cluster"
    
    for modelo in MODELOS_A_TESTEAR:
        print(f"[{modelo}] 🚀 Cargando contexto del modelo...")
        # Modificamos la variable que usa get_llm() en nodes.py
        os.environ["OLLAMA_MODEL"] = modelo
        
        for caso in GOLDEN_DATASET:
            print(f"  -> Ejecutando Test: '{caso['desc']}' (Dificultad: {caso['dificultad']})")
            
            estado_inicial = {
                "alumno_historial": caso["historial"],
                "conceptos_buscados": caso["conceptos"],
                "dificultad": caso["dificultad"],
                "tarea": caso["tarea"],
                "con_solucion": False,
                "lenguaje": "Python",
                "reintentos": 0,
                "criticas_senado": "",
                "ejercicio_generado": ""
            }
            
            inicio = time.time()
            try:
                # Lanzamos el grafo en entorno asíncrono puro
                estado_final = await app.ainvoke(estado_inicial)
                latencia = time.time() - inicio
                
                reintentos = estado_final.get("reintentos", 0)
                ejercicio_final = estado_final.get("enunciado_generado", "")
                
                if ejercicio_final:
                    estado_str = "Aprobado"
                    intentos_totales = reintentos + 1
                else:
                    estado_str = "Rechazado (Límite)"
                    intentos_totales = reintentos
                    ejercicio_final = "Falló la votación del Senado. Límite de reintentos superado."
                
                print(f"     ✅ {estado_str} en {latencia:.2f}s (Intentos: {intentos_totales})")
                
            except Exception as e:
                latencia = time.time() - inicio
                estado_str = "Error"
                intentos_totales = 0
                ejercicio_final = f"Excepción durante el grafo: {str(e)}"
                print(f"     ❌ Error en {latencia:.2f}s: {e}")
            
            resultados.append({
                "Modelo": modelo,
                "Caso_Test": caso["desc"],
                "Dificultad": caso["dificultad"],
                "Latencia_Segundos": round(latencia, 2),
                "Intentos_Senado": intentos_totales,
                "Status": estado_str,
                "Ejercicio": ejercicio_final
            })
            
    # Exportación
    csv_filename = "resultados_benchmark.csv"
    # Guardamos en la raíz del proyecto para fácil acceso
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', csv_filename)
    
    print(f"\n📊 Exportando métricas científicas a {csv_filename}...")
    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            campos = ["Modelo", "Caso_Test", "Dificultad", "Latencia_Segundos", "Intentos_Senado", "Status", "Ejercicio"]
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"✅ Exportación completada con éxito. Archivo CSV listo en la raíz del repositorio.")
    except Exception as e:
        print(f"❌ Error al guardar el archivo CSV: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_benchmark())
