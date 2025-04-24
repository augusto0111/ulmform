#!/bin/bash

echo "🔧 Instalando dependencias necesarias..."
apt-get update && apt-get install -y cmake git build-essential

echo "📥 Clonando CuraEngine..."
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

echo "🛠️ Compilando CuraEngine..."
cmake .
make

echo "📦 Moviendo binario a carpeta /bin..."
mkdir -p ../bin
cp CuraEngine ../bin/CuraEngine

echo "✅ Listo. Archivos en /bin:"
ls -la ../bin
