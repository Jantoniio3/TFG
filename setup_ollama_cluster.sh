#!/bin/bash

echo "==========================================================="
echo "🛠️ SETUP Y ACTUALIZADOR DE OLLAMA PARA CLÚSTER COMPARTIDO"
echo "==========================================================="

echo "Este script configurará Ollama de forma aislada en tu usuario."
echo "¿Qué puerto quieres utilizar para no chocar con tus compañeros?"
read -p "Introduce el puerto (Enter para usar 13434): " PUERTO
PUERTO=${PUERTO:-13434}

echo -e "\n🗑️ 1. Eliminando cualquier instalación anterior..."
rm -rf $HOME/.local/lib/ollama $HOME/.local/bin/ollama

echo "⬇️ 2. Descargando y extrayendo Ollama con zstd..."
# Crear el directorio base por si no existe
mkdir -p $HOME/.local
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst | zstd -d | tar -xf - -C $HOME/.local

echo "⚙️ 3. Configurando variables persistentes en ~/.bashrc..."
# Añadimos las variables solo si no existen ya para no llenar el bashrc de basura
if ! grep -q "OLLAMA_HOST=localhost:$PUERTO" ~/.bashrc; then
    echo "export OLLAMA_HOST=localhost:$PUERTO" >> ~/.bashrc
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=$HOME/.local/lib/ollama:$LD_LIBRARY_PATH' >> ~/.bashrc
fi

echo "✨ 4. Creando el alias 'update-ollama'..."
if ! grep -q "alias update-ollama" ~/.bashrc; then
    echo "alias update-ollama='rm -rf \$HOME/.local/lib/ollama \$HOME/.local/bin/ollama && curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst | zstd -d | tar -xf - -C \$HOME/.local && echo \"✅ Ollama actualizado correctamente\"'" >> ~/.bashrc
fi

echo "==========================================================="
echo "✅ Instalación completada con éxito."
echo "⚠️ IMPORTANTE: Para que los cambios hagan efecto ahora mismo, ejecuta:"
echo "   source ~/.bashrc"
echo ""
echo "En el futuro, cuando quieras actualizar Ollama, solo tendrás que escribir:"
echo "   update-ollama"
echo "==========================================================="
