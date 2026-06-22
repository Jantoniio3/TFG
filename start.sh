

echo "============================================="
echo "INICIANDO ENTORNO TFG SEGURO"
echo "============================================="

echo "0. Verificando instalación de Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama no detectado. Instalando automáticamente en tu espacio de usuario..."
    mkdir -p $HOME/.local
    curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst | zstd -d | tar -xf - -C $HOME/.local
    export PATH=$HOME/.local/bin:$PATH
    export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH
    echo "Instalación completada."
else
    echo "Ollama ya está instalado."
fi

echo "1. Buscando y eliminando servidores Ollama zombie..."
pkill -u $USER -f "ollama serve"

sleep 1 

echo "2. Arrancando el motor de IA limpio en segundo plano..."
ollama serve > ollama_logs.txt 2>&1 &
sleep 3
MODELO=$(grep OLLAMA_MODEL .env.cluster | grep -v OLLAMA_SENATE_MODEL | cut -d '=' -f2)
MODELO_SENADO=$(grep OLLAMA_SENATE_MODEL .env.cluster | cut -d '=' -f2)

echo "Verificando/Descargando el modelo principal $MODELO..."
ollama pull $MODELO

if [ -n "$MODELO_SENADO" ]; then
    echo "Verificando/Descargando el modelo del Senado $MODELO_SENADO..."
    ollama pull "$MODELO_SENADO"
fi

echo "3. Verificando entorno de Python..."
if [ ! -f ".venv_cluster/bin/activate" ]; then
    echo "Entorno virtual no encontrado. Creándolo desde cero e instalando dependencias..."
    python3 -m venv .venv_cluster
    source .venv_cluster/bin/activate
    pip install -r requirements.txt
    echo "Dependencias instaladas."
else

    source .venv_cluster/bin/activate
fi

echo "4. Sincronizando variables de entorno para el Clúster..."
cp .env.cluster .env

echo "5. ¡Todo listo! Arrancando el programa principal..."
echo "============================================="
sleep 5
clear
python main.py
