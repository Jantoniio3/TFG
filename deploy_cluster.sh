#!/bin/bash
echo "==============================================="
echo "🚀 PREPARANDO CLÚSTER PARA EL TUTOR MULTI-AGENTE"
echo "==============================================="

# 1. Configurar el .env
if [ ! -f .env ]; then
    echo "📋 Copiando configuración del cluster (.env.cluster) -> .env..."
    cp .env.cluster .env
else
    echo "⚠️ Ya existe un archivo .env. Asegúrate de modificarlo con las variables de .env.cluster!"
fi

# 2. Creación y activación de entorno virtual (aislado del sistema operativo)
if [ ! -d ".venv_cluster" ]; then
    echo "🐍 Inicializando entorno virtual aislado (.venv_cluster)..."
    python3 -m venv .venv_cluster
fi

echo "🔄 Activando el entorno virtual..."
source .venv_cluster/bin/activate

echo "📦 Instalando dependencias del proyecto..."
pip install -r requirements.txt

# 3. Pulling del modelo gigantesco de Llama...
echo "🦙 Asegurando que llama3.1 de 70B parámetros esté descargado..."
ollama pull llama3.1:70b

echo ""
echo "✅ DEPLOYMENT PREPARADO. Todo listo."
echo "Para arrancar el proyecto en el futuro, RECUERDA ACTIVAR TU ENTORNO SIEMPRE ejecutando:"
echo "source .venv_cluster/bin/activate"
echo "Y luego ya lanzas: python main.py"
