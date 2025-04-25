#!/bin/bash

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
curl -L -o /tmp/CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-amd64

echo "🚚 Otorgando permisos de ejecución"
chmod +x /tmp/CuraEngine

echo "✅ CuraEngine listo para usar desde /tmp"
