#!/bin/bash

echo "🧪 INICIANDO SCRIPT build_cura.sh"

# 🧱 Instalar dependencias necesarias
apt-get update && apt-get install -y cmake git build-essential

# 📦 Clonar y compilar CuraEngine
git clone https://github.com/Ultimaker/CuraEngine.git
cd CuraEngine || exit 1

cmake .
make || { echo "❌ Error en make, CuraEngine no se compiló"; exit 1; }

# 📂 Mostrar si el binario se creó correctamente
echo "📂 Contenido de carpeta CuraEngine:"
ls -la

# 📁 Crear la carpeta bin si no existe
mkdir -p ../bin

# 📤 Copiar el binario a la carpeta bin
cp CuraEngine ../bin/CuraEngine || { echo "❌ Error al copiar CuraEngine"; exit 1; }

# 🔍 Verificar si el binario se copió
echo "📦 Contenido de ./bin:"
ls -la ../bin
