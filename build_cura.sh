#!/bin/bash

echo "🧹 Limpiando residuos anteriores (si existen)..."
rm -rf CuraEngine  # Por si quedó algo de builds anteriores

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
curl -L -o CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-amd64

echo "🚚 Otorgando permisos de ejecución"
chmod +x CuraEngine

mkdir -p bin
mv CuraEngine bin/

echo "✅ CuraEngine listo para usar desde ./bin"
