#!/bin/bash
set -e

echo "🔧 Clonando CuraEngine con submódulos..."
git clone --recurse-submodules https://github.com/Ultimaker/CuraEngine.git

cd CuraEngine

echo "🛠️ Compilando CuraEngine..."
mkdir -p build
cd build
cmake ..
make

cd ../..

echo "📦 Copiando ejecutable a ./bin/"
mkdir -p bin
cp CuraEngine/build/CuraEngine bin/

echo "✅ CuraEngine compilado y copiado exitosamente."
