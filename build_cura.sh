#!/bin/bash
set -e

echo "📥 Descargando CuraEngine precompilado versión 5.4.0..."
mkdir -p ./bin

# Descarga el binario de CuraEngine para Linux desde el repositorio oficial
curl -L -o ./bin/CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.4.0/CuraEngine-linux

# Da permisos de ejecución
chmod +x ./bin/CuraEngine

echo "✅ CuraEngine descargado y listo para usar."
