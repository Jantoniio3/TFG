#!/bin/bash

echo "============================================="
echo "🧪 INICIANDO EL LABORATORIO DE STRESS TESTING 🧪"
echo "============================================="

# Aseguramos que la ruta a Ollama (si se instaló en local) esté disponible
export PATH=$HOME/.local/bin:$PATH
export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH

echo "⚠️ 1. Limpiando procesos zombies de Ollama..."
pkill -u $USER -f "ollama serve"
sleep 2

echo "🚀 2. Levantando Ollama limpio en segundo plano..."
export OLLAMA_NUM_PARALLEL=1
ollama serve > ollama_stress_log.txt 2>&1 &
sleep 4

echo "🐍 3. Activando entorno virtual..."
if [ ! -d ".venv_cluster" ]; then
    echo "❌ ERROR: Entorno virtual no encontrado."
    echo "Por favor, ejecuta 'bash start.sh' al menos una vez para que se instale el entorno."
    exit 1
fi
source .venv_cluster/bin/activate

echo "⚙️ 4. Sincronizando variables de entorno..."
cp .env.cluster .env

echo "🚀 5. Lanzando el Stress Test..."
echo "============================================="
sleep 2

# Ejecuta el test pasando todos los argumentos que le des al script (.sh) hacia Python ($@)
python src/evaluation/consistency_test.py "$@"
