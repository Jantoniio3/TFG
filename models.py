import subprocess

models = [
    ("llama3.3:70b", "4096"),
    ("qwen2.5-coder:32b", "4096")]

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