# ⚡ Despliegue Rápido en AWS EC2

## 🎯 Opción más simple y confiable para tu proyecto

### Por qué EC2 es la mejor opción:
✅ Chrome funciona perfectamente  
✅ Control total del servidor  
✅ Selenium sin restricciones  
✅ Fácil de debugear  

---

## 📝 Pasos Rápidos

### 1️⃣ Crear EC2 Instance (5 min)

```
AWS Console → EC2 → Launch Instance

Configuración:
- AMI: Ubuntu Server 22.04 LTS
- Instance Type: t3.medium (2 vCPU, 4 GB RAM)
- Storage: 20 GB
- Key Pair: Crear/descargar tu-key.pem
- Security Group:
  * Port 22 (SSH): Tu IP
  * Port 8080 (HTTP): 0.0.0.0/0
```

**Costo aproximado: $30-35 USD/mes**

---

### 2️⃣ Conectar y Setup (10 min)

```bash
# LOCAL: Conectar por SSH
chmod 400 tu-key.pem
ssh -i tu-key.pem ubuntu@TU-IP-PUBLICA

# EC2: Instalar dependencias básicas
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# EC2: Clonar repositorio
cd ~
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA

# EC2: Instalar Chrome (CRÍTICO)
chmod +x install_chrome_ec2.sh
./install_chrome_ec2.sh

# EC2: Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-production.txt

# EC2: Crear directorios
mkdir -p data/raw/acm data/raw/sage data/processed
```

---

### 3️⃣ Probar Manualmente (5 min)

```bash
# EC2: Ejecutar servidor
export ENVIRONMENT=production
python webui.py

# LOCAL: Abrir en navegador
http://TU-IP-PUBLICA:8080

# Probar ejecutar Req1 - debe funcionar!
```

---

### 4️⃣ Configurar como Servicio (5 min)

```bash
# EC2: Crear servicio systemd
sudo nano /etc/systemd/system/bibliometria.service
```

Copiar esto:

```ini
[Unit]
Description=Bibliometria Web App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Bibliometria_AA
Environment="PATH=/home/ubuntu/Bibliometria_AA/venv/bin"
Environment="ENVIRONMENT=production"
Environment="PORT=8080"
ExecStart=/home/ubuntu/Bibliometria_AA/venv/bin/gunicorn webui:app --bind 0.0.0.0:8080 --timeout 600 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bibliometria
sudo systemctl start bibliometria
sudo systemctl status bibliometria
```

---

### ✅ ¡LISTO!

Tu aplicación ahora está:
- ✅ Ejecutándose 24/7
- ✅ Se reinicia automáticamente si falla
- ✅ Accesible desde http://TU-IP:8080

---

## 🐛 Si algo falla:

```bash
# Ver logs
sudo journalctl -u bibliometria -f

# Reiniciar servicio
sudo systemctl restart bibliometria

# Probar Chrome
google-chrome --version
```

---

## 🔒 Opcional: Agregar HTTPS

```bash
# Instalar Nginx + Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Configurar dominio (debes tener un dominio apuntando a tu IP)
sudo certbot --nginx -d tu-dominio.com

# Nginx automáticamente hace proxy a :8080 con SSL
```

---

## 💰 Costos

| Recurso | Precio/mes |
|---------|------------|
| EC2 t3.medium | ~$30 |
| Elastic IP | $3.60 |
| Storage 20GB | $2 |
| **TOTAL** | **~$35** |

💡 Tip: Apaga la instancia cuando no la uses para ahorrar

---

## 📚 Más Ayuda

- **Guía completa**: `DEPLOYMENT_AWS.md`
- **Errores comunes**: `AWS_TROUBLESHOOTING.md`
- **Probar local**: `bash test_production.sh`

---

## ⚠️ IMPORTANTE: .venv

**NO subas `.venv/` a Git** - ya está en `.gitignore`

Cada servidor (local, EC2, etc.) debe crear su propio venv:
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt
```

---

¿Problemas? Revisa `AWS_TROUBLESHOOTING.md` o pregúntame!
