import subprocess

# Define aquí la lista de modelos que quieres probar y su contexto asociado
# Formato: ("nombre_del_modelo", "tamaño_contexto")
models = [
    ("qwen2.5:72b", "16384"),
    ("deepseek-r1:70b", "16384"),
    ("llama3.3:70b", "16384"),
    ("llama3.1:70b", "16384"),
    ("qwen2.5-coder:32b", "65536"),
    ("codestral:22b", "65536"),
    ("deepseek-coder-v2:16b", "65536"),
    ("phi4:14b", "65536")
]

iteraciones = 10

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