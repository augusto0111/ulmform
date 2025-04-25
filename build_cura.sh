#!/bin/bash

echo "🧹 Limpiando residuos anteriores (si existen)..."
rm -f /tmp/CuraEngine

echo "📥 Descargando CuraEngine precompilado (v5.2.11)..."
curl -L -o /tmp/CuraEngine https://github.com/Ultimaker/CuraEngine/releases/download/5.2.11/CuraEngine-linux-amd64

echo "🚚 Otorgando permisos de ejecución..."
chmod +x /tmp/CuraEngine

echo "✅ CuraEngine listo para usar desde /tmp"
