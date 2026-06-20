"""Modo de evaluación exclusivo para el Senado Reflexivo.

Ejecuta el pipeline de generación 10 veces para un modelo dado,
registrando la nota que le otorga cada uno de los 3 jueces del senado
y su nota media final, para analizar la severidad y varianza de la IA.
"""

import os
import sys
import time
import csv
import asyncio
from dotenv import load_dotenv

# Asegurar que el path alcanza la raíz
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.graph import build_graph

async def run_senate_eval(N: int = 10):
    print("=" * 60)
    print(f"🏛️ INICIANDO EVALUACIÓN DEL SENADO (N={N})")
    print("=" * 60)
    
    app = build_graph()
    
    load_dotenv()
    if len(sys.argv) > 2:
        modelo = sys.argv[2]
        os.environ["OLLAMA_MODEL"] = modelo
    else:
        modelo = os.getenv("OLLAMA_MODEL", "Desconocido")
        
    csv_filename = "senate_evalution.csv"
    headers = [
        "Iteracion", 
        "Modelo", 
        "Conceptos",
        "Juez_1_Nota",
        "Juez_2_Nota",
        "Juez_3_Nota",
        "Nota_Media", 
        "Reintentos", 
        "Resultado_Final"
    ]
    
    file_exists = os.path.isfile(csv_filename) and os.path.getsize(csv_filename) > 0
    
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        if not file_exists:
            writer.writerow(headers)
            
        for i in range(1, N + 1):
            conceptos = ["Recursividad", "Bucle for", "Funciones"]
            print(f"\n[{i}/{N}] Generando y evaluando con el Senado Reflexivo...")
            
            initial_state = {
                "tarea": "generar",
                "con_solucion": False,
                "lenguaje": "Python",
                "codigo_entrada": "",
                "resultado_codigo": "",
                "alumno_historial": ["Variable", "Tipo de dato", "Función", "Sentencia condicional", "Bucle for", "Bucle while", "Recursividad"],
                "conceptos_buscados": conceptos,
                "dificultad": "Media",
                "ejercicios_contexto": [],
                "enunciado_generado": "",
                "codigo_solucion": "",
                "explicacion": "",
                "reintentos": 0,
                "ejercicio_generado": "",
                "criticas_senado": "",
                "votos_senado": "",
                "nota_senado": 0.0,
                "notas_individuales": [],
                "modo_desarrollador": False,
                "usar_senado": True,
                "tipo_senado": "reflexion"
            }
            
            async for s in app.astream(initial_state, config={"recursion_limit": 20}):
                for node_name, node_state in s.items():
                    initial_state.update(node_state)
            
            final_state = initial_state
            
            # Extraer notas individuales
            notas = final_state.get("notas_individuales", [])
            j1 = notas[0] if len(notas) > 0 else 0
            j2 = notas[1] if len(notas) > 1 else 0
            j3 = notas[2] if len(notas) > 2 else 0
            
            nota_media = final_state.get("nota_senado", 0.0)
            reintentos = final_state.get("reintentos", 0)
            
            if not final_state.get("criticas_senado"):
                resultado = "Aprobado"
            else:
                resultado = "Rechazado (Límite reintentos)"
                
            print(f"   => Notas: J1({j1}) - J2({j2}) - J3({j3}) | MEDIA: {nota_media}/10 | Reintentos: {reintentos} | {resultado}")
            
            row = [i, modelo, ", ".join(conceptos), j1, j2, j3, nota_media, reintentos, resultado]
            writer.writerow(row)
            f.flush()
            
    print("\n✅ Evaluación del Senado finalizada. Resultados guardados en: senate_evalution.csv")

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(run_senate_eval(N))
