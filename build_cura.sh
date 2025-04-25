#!/bin/bash

echo "🧹 Limpiando residuos anteriores (si existen)..."
rm -f ./bin/CuraEngine

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
mkdir -p bin
curl -L -o bin/CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-amd64

echo "🚚 Otorgando permisos de ejecución"
chmod +x bin/CuraEngine

echo "✅ CuraEngine listo para usar desde ./bin"
