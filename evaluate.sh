#!/bin/bash

echo "============================================="
echo "🧪 INICIANDO EL LABORATORIO DE MODELOS 🧪"
echo "============================================="

echo "⚙️ 1. Comprobando servicio de Ollama..."
# Si Ollama no responde, lo levantamos en segundo plano
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Levantando Ollama en segundo plano..."
    ollama serve > ollama_eval_log.txt 2>&1 &
    sleep 3
fi

echo "🐍 2. Activando entorno virtual..."
if [ ! -d ".venv_cluster" ]; then
    echo "❌ ERROR: Entorno virtual no encontrado."
    echo "Por favor, ejecuta 'bash start.sh' al menos una vez para que se instale el entorno y Ollama."
    exit 1
fi
source .venv_cluster/bin/activate

echo "⚙️ 3. Sincronizando variables de entorno..."
cp .env.cluster .env

echo "🚀 4. Lanzando el Evaluador Automático..."
echo "============================================="
sleep 2
clear

python src/evaluation/model_evaluator.py
