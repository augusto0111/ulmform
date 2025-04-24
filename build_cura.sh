#!/bin/bash

# Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# Clonar CuraEngine desde GitHub
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine

# Compilar
cmake .
make

# Mover el binario a la raíz del proyecto
cp CuraEngine ../CuraEngine
