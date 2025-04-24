#!/bin/bash

echo "🔧 Clonando CuraEngine con submódulos..."
git clone --recurse-submodules https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

echo "🛠️ Compilando CuraEngine..."
mkdir build
cd build
cmake ..
make

echo "📦 Copiando ejecutable a ./bin/"
mkdir -p ../../bin
cp CuraEngine ../../bin/CuraEngine

echo "✅ CuraEngine compilado y copiado exitosamente."
