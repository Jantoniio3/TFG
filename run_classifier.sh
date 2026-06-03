#!/bin/bash

echo "============================================="
echo "EJECUTANDO CLASIFICADOR DE EJERCICIOS (LLM)"
echo "============================================="

echo "Verificando entorno de Python..."
if [ -d ".venv_cluster" ]; then
    echo "Activando entorno virtual del clúster..."
    source .venv_cluster/bin/activate
elif [ -d "venv" ]; then
    echo "Activando entorno virtual local..."
    source venv/bin/activate
else
    echo "Aviso: No se detectó un entorno virtual, ejecutando con el python del sistema."
fi

echo "Iniciando clasificación..."
# Usar variable de entorno PYTHONPATH para que los imports de módulos funcionen correctamente
export PYTHONPATH=$PYTHONPATH:$(pwd)

python src/etl/rubric_classifier.py

echo "============================================="
echo "Terminado."
echo "============================================="
