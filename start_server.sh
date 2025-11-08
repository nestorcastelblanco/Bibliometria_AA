#!/bin/bash
# Script para iniciar el servidor Django en producción

echo "🚀 Iniciando servidor Django en Google Cloud VM..."
echo ""
echo "📍 El servidor estará disponible en:"
echo "   - IP Externa VM: http://<TU_IP_EXTERNA>:8000"
echo "   - Dashboard: http://<TU_IP_EXTERNA>:8000/dashboard/"
echo "   - API: http://<TU_IP_EXTERNA>:8000/api/"
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Aplicar migraciones
echo "🔧 Aplicando migraciones..."
python3 manage.py migrate

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python3 manage.py collectstatic --noinput

# Iniciar servidor en todas las interfaces (0.0.0.0)
echo "🌐 Iniciando servidor en 0.0.0.0:8000..."
echo "   Presiona Ctrl+C para detener"
echo ""
python3 manage.py runserver 0.0.0.0:8000
