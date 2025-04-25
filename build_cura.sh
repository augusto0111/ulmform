#!/bin/bash

echo "🧹 Limpiando residuos anteriores (si existen)..."
rm -f ./bin/CuraEngine

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
curl -L -o CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux-x64.AppImage

echo "📦 Desempaquetando AppImage..."
chmod +x CuraEngine
./CuraEngine --appimage-extract > /dev/null

echo "🚚 Moviendo binario CuraEngine extraído..."
mkdir -p ./bin
mv squashfs-root/usr/bin/CuraEngine ./bin/CuraEngine

echo "🔧 Otorgando permisos de ejecución a ./bin/CuraEngine"
chmod +x ./bin/CuraEngine

echo "✅ CuraEngine listo para usar desde ./bin"
