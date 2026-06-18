import subprocess

models = [
    # --- Familia Meta (LLaMA) ---
    ("llama3.3:70b", "4096"),          # El estado del arte actual de Meta. Razonamiento lógico insuperable.
    ("llama3.1:70b", "4096"),          # Versión anterior de Meta. Perfecto para medir si la v3.3 realmente mejora a la v3.1.
    
    # --- Familia Alibaba (Qwen) ---
    ("qwen2.5-coder:32b", "4096"),     # El mejor modelo open-source específico de código en su rango de peso.
    ("qwen2.5:72b", "4096"),           # El hermano mayor genérico. Útil para ver si un modelo genérico de 72B supera a uno de código de 32B.
    
    # --- Modelos especializados en RAG y Código ---
    ("command-r:35b", "4096"),         # Creado por Cohere, está entrenado específicamente para sistemas RAG y uso de herramientas.
    ("deepseek-coder:33b", "4096")     # Un clásico altamente eficiente en la corrección de errores de programación (debug).
]

iteraciones = 5

print("=" * 60)
print("🚀 INICIANDO BATERÍA DE TESTS MULTI-MODELO")
print("=" * 60)

for model, num_ctx in models:
    print(f"\n▶️ Iniciando ronda de evaluación para: {model} (Contexto: {num_ctx})")
    

    comando = ["bash", "run_stress_test.sh", str(iteraciones), model, num_ctx]
    
    try:

        subprocess.run(comando, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Hubo un error al evaluar {model}. Saltando al siguiente...")
        
    print(f"🧹 Borrando el modelo {model} para liberar espacio en disco...")
    subprocess.run(["ollama", "rm", model])

print("\n✅ ¡Toda la batería de modelos ha finalizado! Revisa tu archivo stress_test_results.csv")