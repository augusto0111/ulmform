#!/bin/bash

# Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# Clonar CuraEngine si no existe
if [ ! -d "CuraEngine" ]; then
  git clone https://github.com/Ultimaker/CuraEngine.git
fi

cd CuraEngine

# Compilar
cmake .
make

# Crear carpeta bin en raíz si no existe
mkdir -p ../bin

# Mover el ejecutable compilado a bin/
cp CuraEngine ../bin/CuraEngine
