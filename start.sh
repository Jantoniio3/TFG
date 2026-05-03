#!/bin/bash

echo "============================================="
echo "🚀 INICIANDO ENTORNO TFG SEGURO"
echo "============================================="

echo "🧹 1. Buscando y eliminando servidores Ollama zombie..."
pkill -u $USER -f "ollama serve"
# Damos 1 segundo para asegurar que se libera el puerto
sleep 1 

echo "🧠 2. Arrancando el motor de IA limpio en segundo plano..."
ollama serve > ollama_logs.txt 2>&1 &
# Damos 3 segundos para que Ollama se despierte completamente
sleep 3 

echo "🐍 3. Activando la burbuja de Python..."
# Activamos el entorno virtual. Si usas otro nombre distinto a .venv_cluster, cámbialo aquí
source .venv_cluster/bin/activate

echo "⚙️ 4. Sincronizando variables de entorno para el Clúster..."
cp .env.cluster .env

echo "💻 5. ¡Todo listo! Arrancando el programa principal..."
echo "============================================="
sleep 2
clear
python main.py
