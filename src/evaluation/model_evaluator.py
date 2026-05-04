"""Laboratorio de Evaluación de Modelos (Benchmarking).

Este módulo se encarga de auditar los modelos LLM descargados en la máquina,
evaluando su capacidad matemática y su obediencia al formato JSON estructurado,
ambas capacidades vitales para funcionar como Juez en el Senado de LangGraph.
"""

import os
import sys
from dotenv import load_dotenv
import ollama

# Asegurar que el path alcanza la raíz si se necesita
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

# Conectar al puerto correcto configurado en .env
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
client = ollama.Client(host=ollama_url)

def evaluar_modelos():
    """Escanea la máquina en busca de modelos Ollama y ejecuta una prueba de aptitud.
    
    Se comunica con el servidor Ollama activo, recupera la lista de modelos instalados
    y les envía un prompt trampa (temperature=0.0) exigiéndoles una salida forzada en JSON.
    Genera un informe final por consola clasificando los modelos en APTOS, DUDOSOS o NO APTOS.
    """
    print("=" * 60)
    print("🧪 EVALUADOR AUTOMÁTICO DE APTITUD DE MODELOS")
    print("=" * 60)
    print(f"📡 Conectando al servidor de Ollama en: {ollama_url}")
    
    try:
        modelos_instalados = client.list()
        lista_modelos = [m.model for m in modelos_instalados.models]
        if not lista_modelos:
            print("❌ No se ha encontrado ningún modelo instalado. Usa 'ollama pull <modelo>'.")
            return
            
        print(f"📦 Modelos detectados instalados en tu máquina: {len(lista_modelos)}")
        for m in lista_modelos:
            print(f"   - {m}")
            
    except Exception as e:
        print(f"❌ Error al conectar con Ollama. ¿Está encendido el servidor? ({e})")
        return

    print("\nIniciando test de aptitud a cada modelo...")
    print("(La prueba evalúa si el modelo es capaz de forzar su salida en JSON estricto sin alucinar, vital para el Senado de LangGraph)")
    
    resultados = []
    
    # Prompt trampa que exige tanto razonamiento como estructuración estricta JSON
    prompt_trampa = """Eres un profesor de matemáticas. 
Resuelve el siguiente problema de forma directa y clara.
Problema: Si tienes 2 manzanas y te doy otras 2 manzanas, ¿cuántas manzanas tienes en total?

Debes devolver obligatoriamente un objeto JSON válido con dos claves exactas:
- "resolucion": un string explicando brevemente el cálculo.
- "es_correcto": un booleano (true/false) indicando si la respuesta final es 4.
"""

    for modelo in lista_modelos:
        print(f"\n[{modelo}] 🚀 Evaluando aptitud...")
        try:
            # Usamos la librería nativa para generar la respuesta forzando 'json'
            response = client.generate(
                model=modelo,
                prompt=prompt_trampa,
                format='json',
                options={
                    "temperature": 0.0, # Determinista para evitar florituras
                    "num_ctx": 2048 # Contexto minúsculo para que la evaluación sea ultra rápida
                }
            )
            
            output = response.get('response', '')
            
            # Validación sencilla del output esperado
            has_resolucion = '"resolucion"' in output.lower()
            has_correcto = '"es_correcto"' in output.lower()
            has_true = 'true' in output.lower()
            
            if has_resolucion and has_correcto and has_true:
                estado = "🟢 APTO"
                motivo = "Formato JSON perfecto y lógica matemática validada."
            elif has_resolucion and has_correcto:
                estado = "🟡 DUDOSO"
                motivo = "Devolvió JSON pero falló en la lógica básica (es_correcto != true)."
            else:
                estado = "🔴 NO APTO"
                motivo = "Fue incapaz de estructurar la salida en un JSON válido con las claves pedidas."
                
            print(f"  -> Veredicto: {estado}")
            
        except Exception as e:
            estado = "🔴 NO APTO"
            motivo = f"Excepción durante la prueba: {str(e)}"
            print(f"  -> Veredicto: {estado} (Error: {str(e)})")
            
        resultados.append({"modelo": modelo, "estado": estado, "motivo": motivo})
        
    # Tabla final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DE APTITUD PARA EL SISTEMA MULTI-AGENTE")
    print("=" * 80)
    print(f"{'MODELO':<25} | {'VEREDICTO':<12} | {'MOTIVO'}")
    print("-" * 80)
    for res in resultados:
        print(f"{res['modelo']:<25} | {res['estado']:<12} | {res['motivo']}")

if __name__ == "__main__":
    evaluar_modelos()
