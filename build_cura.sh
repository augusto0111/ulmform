#!/bin/bash

# Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# Clonar CuraEngine desde GitHub
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

# Compilar
cmake .
make

# Crear carpeta bin y mover el ejecutable
mkdir -p ../bin
cp CuraEngine ../bin/CuraEngine
