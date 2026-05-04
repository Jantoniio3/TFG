#!/bin/bash

echo "============================================="
echo "🧪 INICIANDO EL LABORATORIO DE MODELOS 🧪"
echo "============================================="

# Aseguramos que la ruta a Ollama (si se instaló en local) esté disponible
export PATH=$HOME/.local/bin:$PATH
export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH

echo "⚙️ 1. Comprobando servicio de Ollama..."
# Si Ollama no responde, matamos zombies y lo levantamos en segundo plano
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️ Ollama no responde. Limpiando procesos zombies..."
    pkill -u $USER -f "ollama serve"
    sleep 2
    
    echo "🚀 Levantando Ollama en segundo plano..."
    ollama serve > ollama_eval_log.txt 2>&1 &
    sleep 4
fi

echo "🐍 2. Activando entorno virtual..."
if [ ! -d ".venv_cluster" ]; then
    echo "❌ ERROR: Entorno virtual no encontrado."
    echo "Por favor, ejecuta 'bash start.sh' al menos una vez para que se instale el entorno."
    exit 1
fi
source .venv_cluster/bin/activate

echo "⚙️ 3. Sincronizando variables de entorno..."
cp .env.cluster .env

echo "🚀 4. Lanzando el Evaluador Automático..."
echo "============================================="
sleep 2

# Quitamos el 'clear' para que puedas leer si hubo algún error en los pasos anteriores
python src/evaluation/model_evaluator.py
