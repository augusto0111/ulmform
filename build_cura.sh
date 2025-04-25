#!/bin/bash

echo "🧹 Limpiando residuos anteriores (si existen)..."
rm -f ./bin/CuraEngine

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "📁 Creando carpeta ./bin si no existe..."
mkdir -p ./bin

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
curl -L -o ./bin/CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-x64

echo "🚚 Otorgando permisos de ejecución"
chmod +x ./bin/CuraEngine

echo "✅ CuraEngine listo para usar desde ./bin/CuraEngine"
