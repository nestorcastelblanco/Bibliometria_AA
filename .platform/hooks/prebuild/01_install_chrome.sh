#!/bin/bash
# Script para instalar Chrome y ChromeDriver en AWS EC2/Elastic Beanstalk

echo "🔧 Instalando Google Chrome..."

# Descargar e instalar Chrome
curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Verificar instalación
google-chrome --version

echo "✅ Chrome instalado correctamente"
