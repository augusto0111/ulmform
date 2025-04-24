#!/bin/bash

# Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# Clonar y compilar CuraEngine
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine
cmake .
make

# Mostrar si el binario se creó
echo "📁 Contenido de carpeta CuraEngine:"
ls -la

# Crear la carpeta bin si no existe
mkdir -p ../bin

# Mover el binario
cp CuraEngine ../bin/

# Verificamos si el binario se copió
echo "📁 Contenido de ./bin:"
ls -la ../bin
