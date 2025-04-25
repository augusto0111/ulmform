#!/bin/bash

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install gunicorn

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
curl -L -o CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-amd64

echo "🚚 Moviendo CuraEngine a ./bin/"
mkdir -p bin
mv CuraEngine bin/CuraEngine
chmod +x bin/CuraEngine

echo "✅ CuraEngine descargado y listo para usar."
