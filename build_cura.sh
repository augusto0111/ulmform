#!/bin/bash
set -e  # Detener el script ante cualquier error

echo "🔧 Instalando dependencias..."
apt-get update && apt-get install -y cmake git build-essential

echo "📥 Clonando CuraEngine..."
git clone https://github.com/Ultimaker/CuraEngine.git

cd CuraEngine

echo "🛠️ Compilando CuraEngine..."
cmake .
make

echo "📦 Listando contenido compilado:"
ls -la

echo "📁 Creando carpeta bin en la raíz del proyecto..."
mkdir -p ../bin

echo "📂 Moviendo CuraEngine compilado a ./bin/"
cp CuraEngine ../bin/CuraEngine

cd ..

echo "📁 Estructura completa del proyecto:"
ls -R

echo "✅ Compilación finalizada correctamente."
