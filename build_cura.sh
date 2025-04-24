#!/bin/bash

# Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# Clonar CuraEngine
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

# Compilar
cmake .
make

# Crear carpeta bin si no existe y copiar
mkdir -p ../bin
cp CuraEngine ../bin/CuraEngine
