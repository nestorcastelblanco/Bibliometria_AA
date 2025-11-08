#!/bin/bash
# Script para configurar el servicio systemd de Bibliometria

echo "🚀 Configurando servicio systemd para Bibliometria..."

# Copiar archivo de servicio
sudo cp /home/sebastian_agudelom/Bibliometria_AA/deploy/bibliometria.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio para inicio automático
sudo systemctl enable bibliometria.service

# Iniciar servicio
sudo systemctl start bibliometria.service

# Verificar estado
sudo systemctl status bibliometria.service

echo ""
echo "✅ Servicio configurado!"
echo ""
echo "📝 Comandos útiles:"
echo "  sudo systemctl status bibliometria    # Ver estado"
echo "  sudo systemctl restart bibliometria   # Reiniciar"
echo "  sudo systemctl stop bibliometria      # Detener"
echo "  sudo systemctl start bibliometria     # Iniciar"
echo "  sudo journalctl -u bibliometria -f    # Ver logs en tiempo real"
echo ""
echo "🌐 Dashboard disponible en: http://136.119.148.160:8000/"
