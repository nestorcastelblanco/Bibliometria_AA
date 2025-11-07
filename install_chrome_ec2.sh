#!/bin/bash
# Script de instalación de Chrome para Amazon Linux 2023 / Ubuntu en EC2

set -e

echo "🚀 Instalando dependencias para Chrome en AWS EC2..."

# Detectar el sistema operativo
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

if [[ "$OS" == "amzn" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "centos" ]]; then
    # Amazon Linux / RHEL / CentOS
    echo "📦 Detectado: $OS"
    
    sudo yum update -y
    sudo yum install -y wget unzip xorg-x11-server-Xvfb gtk3 dbus-glib
    
    # Descargar Chrome
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    sudo yum install -y ./google-chrome-stable_current_x86_64.rpm
    rm google-chrome-stable_current_x86_64.rpm
    
elif [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    # Ubuntu / Debian
    echo "📦 Detectado: $OS"
    
    sudo apt-get update
    sudo apt-get install -y wget unzip xvfb libgtk-3-0 libdbus-glib-1-2
    
    # Agregar repositorio de Chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
else
    echo "❌ Sistema operativo no soportado: $OS"
    exit 1
fi

# Verificar instalación
if command -v google-chrome &> /dev/null; then
    echo "✅ Chrome instalado correctamente:"
    google-chrome --version
else
    echo "❌ Error: Chrome no se instaló correctamente"
    exit 1
fi

echo ""
echo "✅ Instalación completa!"
echo "💡 Ahora puedes ejecutar los scrapers en modo headless"
