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

# 2. Instalar el entorno (Asumiendo que has creado un conda o venv nuevo en el linux)
echo "📦 Instalando dependencias del proyecto..."
pip install -r requirements.txt

# 3. Pulling del modelo gigantesco de Llama...
echo "🦙 Asegurando que llama3.1 de 70B parámetros esté descargado..."
ollama pull llama3.1:70b

echo ""
echo "✅ DEPLOYMENT PREPARADO. Todo listo para iniciar."
echo "Si es tu primer inicio, no olvides ejecutar: python src/scripts/init_ontology.py"
echo "Para arrancar la interfaz completa: python main.py"
