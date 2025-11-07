#!/bin/bash
# Script para probar la aplicación antes de desplegar en AWS

set -e

echo "🧪 Probando configuración de producción localmente..."
echo ""

# Verificar que Chrome está instalado
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "⚠️  ADVERTENCIA: Chrome/Chromium no detectado"
    echo "    En macOS esto es normal - la prueba headless puede fallar"
    echo "    En AWS EC2 debes instalar Chrome con install_chrome_ec2.sh"
    echo ""
fi

# Activar entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ ERROR: No se encuentra .venv"
    echo "   Ejecuta: python3.11 -m venv .venv"
    exit 1
fi

source .venv/bin/activate

# Verificar dependencias
echo "📦 Verificando dependencias..."
pip install -q -r requirements-production.txt

# Probar importación de módulos críticos
echo "🔍 Probando importaciones..."
python3 -c "
import undetected_chromedriver as uc
import flask
import selenium
print('✅ Módulos críticos OK')
"

# Probar modo headless
echo ""
echo "🎭 Probando modo headless..."
ENVIRONMENT=production python3 -c "
import os
os.environ['ENVIRONMENT'] = 'production'
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

print('   Iniciando Chrome en modo headless...')
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = uc.Chrome(options=options, version_main=None)
    driver.get('https://www.google.com')
    title = driver.title
    driver.quit()
    print(f'   ✅ Headless OK - Título: {title}')
except Exception as e:
    print(f'   ⚠️  Headless falló: {e}')
    print('   Esto es normal en macOS - funcionará en Linux/AWS')
"

# Probar que Flask arranca
echo ""
echo "🌐 Probando servidor Flask..."
ENVIRONMENT=production PORT=8080 timeout 5 python3 webui.py &
PID=$!
sleep 3

if ps -p $PID > /dev/null; then
    echo "   ✅ Flask arrancó correctamente"
    kill $PID
else
    echo "   ❌ Flask no arrancó"
    exit 1
fi

echo ""
echo "✅ TODAS LAS PRUEBAS PASARON!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Revisar DEPLOYMENT_AWS.md para instrucciones completas"
echo "   2. Asegurarte que .venv está en .gitignore"
echo "   3. Hacer commit de los archivos nuevos:"
echo "      git add ."
echo "      git commit -m 'Preparar para despliegue en AWS'"
echo "      git push origin deployment"
echo ""
