#!/bin/bash

echo "🧹 Limpiando residuos anteriores..."
rm -rf CuraEngine build || true

echo "📥 Clonando CuraEngine desde GitHub (versión 5.4.0)..."
git clone --branch 5.4.0 https://github.com/Ultimaker/CuraEngine.git

echo "🛠️ Compilando CuraEngine con CMake..."
apt-get update && apt-get install -y cmake g++ make

mkdir -p CuraEngine/build
cd CuraEngine/build
cmake ..
make

echo "🚚 Moviendo ejecutable a /tmp para uso en la app..."
cp CuraEngine /tmp/CuraEngine
chmod +x /tmp/CuraEngine

echo "✅ CuraEngine compilado y listo en /tmp/CuraEngine"
