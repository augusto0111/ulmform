#!/bin/bash

# ✅ Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# ✅ Clonar y compilar CuraEngine
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine
cmake .
make

# ✅ Mostrar si el binario se creó correctamente
echo "📂 Contenido de carpeta CuraEngine:"
ls -la

# ✅ Crear la carpeta bin en la raíz si no existe
mkdir -p ./bin

# ✅ Copiar el binario a la carpeta bin
cp CuraEngine ./bin/CuraEngine

# ✅ Verificar si el binario se copió
echo "📦 Contenido de ./bin:"
ls -la ./bin/
