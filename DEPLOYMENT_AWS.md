# 🚀 Guía de Despliegue en AWS

## ⚠️ ADVERTENCIAS IMPORTANTES

### Problema Principal: Selenium + Chrome
Tu aplicación usa **Selenium con undetected-chromedriver**, lo cual presenta desafíos en AWS:

1. **Chrome no viene instalado** en AWS por defecto
2. **Requiere modo headless** (sin interfaz gráfica)
3. **Consume muchos recursos** (CPU/RAM)
4. **Timeouts largos** - los scrapers pueden tardar 10-15 minutos

### Opciones de Despliegue

| Opción | Ventajas | Desventajas | Recomendado |
|--------|----------|-------------|-------------|
| **AWS EC2** | Control total, Chrome funciona bien | Más caro, requiere mantenimiento | ✅ **SÍ** |
| AWS Lambda | Serverless, barato | Límite de 15 min, difícil instalar Chrome | ❌ NO |
| AWS Elastic Beanstalk | Fácil deploy | Chrome requiere configuración especial | ⚠️ Complicado |
| AWS ECS/Docker | Escalable | Requiere conocimiento de Docker | ⚠️ Avanzado |

---

## 📋 OPCIÓN 1: AWS EC2 (RECOMENDADO)

### Paso 1: Crear instancia EC2

```bash
# En AWS Console:
# 1. Ir a EC2 > Launch Instance
# 2. Seleccionar: Ubuntu Server 22.04 LTS
# 3. Tipo: t3.medium o superior (2 vCPUs, 4 GB RAM mínimo)
# 4. Almacenamiento: 20 GB mínimo
# 5. Security Group: Permitir puerto 8080 (HTTP custom)
# 6. Crear/descargar key pair (.pem)
```

### Paso 2: Conectar y configurar

```bash
# Conectar por SSH (reemplaza con tu key y IP)
chmod 400 tu-key.pem
ssh -i tu-key.pem ubuntu@tu-ip-publica

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y git
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### Paso 3: Clonar repositorio

```bash
cd ~
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
```

### Paso 4: Instalar Chrome

```bash
# Ejecutar el script de instalación
chmod +x install_chrome_ec2.sh
./install_chrome_ec2.sh
```

### Paso 5: Configurar aplicación

```bash
# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements-production.txt

# Crear directorios necesarios
mkdir -p data/raw/acm data/raw/sage data/processed
```

### Paso 6: Configurar variables de entorno

```bash
# Crear archivo .env
cat > .env << EOF
ENVIRONMENT=production
PORT=8080
FLASK_APP=webui.py
EOF
```

### Paso 7: Ejecutar en producción

```bash
# Opción A: Ejecutar directamente (para pruebas)
export ENVIRONMENT=production
python webui.py

# Opción B: Usar Gunicorn (recomendado)
gunicorn webui:app --bind 0.0.0.0:8080 --timeout 600 --workers 2 --daemon

# Opción C: Usar systemd (mejor para producción)
# Ver sección "Configurar como Servicio" más abajo
```

### Paso 8: Acceder a la aplicación

```
http://tu-ip-publica:8080
```

---

## 🔧 Configurar como Servicio (systemd)

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/bibliometria.service
```

Contenido:

```ini
[Unit]
Description=Bibliometria Web Application
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bibliometria
sudo systemctl start bibliometria
sudo systemctl status bibliometria

# Ver logs
sudo journalctl -u bibliometria -f
```

---

## 🐳 OPCIÓN 2: Docker + ECS (Avanzado)

### Paso 1: Crear Dockerfile

Ya está creado en el repositorio. Ver archivo `Dockerfile`.

### Paso 2: Construir imagen

```bash
docker build -t bibliometria-app .
docker run -p 8080:8080 bibliometria-app
```

### Paso 3: Subir a ECR

```bash
# Autenticar con ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin TU_CUENTA.dkr.ecr.us-east-1.amazonaws.com

# Crear repositorio
aws ecr create-repository --repository-name bibliometria-app

# Tag y push
docker tag bibliometria-app:latest TU_CUENTA.dkr.ecr.us-east-1.amazonaws.com/bibliometria-app:latest
docker push TU_CUENTA.dkr.ecr.us-east-1.amazonaws.com/bibliometria-app:latest
```

---

## 🔒 Configuración de Seguridad

### Security Group (EC2)

```
Inbound Rules:
- Port 22 (SSH): Tu IP solamente
- Port 8080 (HTTP): 0.0.0.0/0 (o tu IP si es privado)
- Port 443 (HTTPS): 0.0.0.0/0 (si usas SSL)
```

### Nginx (Opcional - para SSL)

```bash
sudo apt install -y nginx certbot python3-certbot-nginx

# Configurar Nginx
sudo nano /etc/nginx/sites-available/bibliometria
```

Contenido:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 600s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/bibliometria /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com
```

---

## 🐛 Troubleshooting

### Chrome no se ejecuta

```bash
# Verificar instalación
google-chrome --version

# Verificar que undetected-chromedriver funcione
python3 -c "import undetected_chromedriver as uc; uc.Chrome(headless=True)"
```

### Error de permisos

```bash
# Dar permisos a directorios
chmod -R 755 ~/Bibliometria_AA/data
chown -R ubuntu:ubuntu ~/Bibliometria_AA
```

### Scrapers muy lentos

```bash
# Aumentar recursos de EC2
# Cambiar a instancia más grande (t3.large o t3.xlarge)
```

### Logs de errores

```bash
# Ver logs de aplicación
tail -f ~/Bibliometria_AA/*.log

# Ver logs del sistema
sudo journalctl -u bibliometria -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 💰 Estimación de Costos

| Recurso | Tipo | Costo Mensual (aprox) |
|---------|------|----------------------|
| EC2 t3.medium | On-Demand | ~$30 USD |
| EC2 t3.large | On-Demand | ~$60 USD |
| Elastic IP | Fijo | $3.60 USD |
| EBS Storage 20GB | SSD | $2 USD |
| **TOTAL** | | **~$35-65 USD/mes** |

💡 **Tip**: Usa Reserved Instances para ahorrar hasta 40%

---

## ✅ Checklist Final

Antes de declarar el deployment exitoso:

- [ ] Chrome instalado y funcionando
- [ ] Scrapers ejecutan sin errores
- [ ] Web UI accesible desde internet
- [ ] Gráficos se generan correctamente
- [ ] Logs se están guardando
- [ ] Servicio se reinicia automáticamente
- [ ] Security Group configurado correctamente
- [ ] Backups configurados (opcional)
- [ ] Monitoring configurado (CloudWatch)

---

## 📞 Problemas Comunes

### 1. "Chrome binary not found"
```bash
# Reinstalar Chrome
./install_chrome_ec2.sh
```

### 2. "Memory error"
```bash
# Aumentar swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. "Module not found"
```bash
# Reinstalar dependencias
source venv/bin/activate
pip install -r requirements-production.txt
```

---

## 🎯 Próximos Pasos Recomendados

1. **Configurar dominio personalizado** (Route 53)
2. **Implementar SSL/HTTPS** (Let's Encrypt + Nginx)
3. **Configurar backups automáticos** (AWS Backup)
4. **Implementar monitoring** (CloudWatch + alertas)
5. **Optimizar costos** (Reserved Instances, Auto Scaling)
6. **CI/CD** (GitHub Actions para deployment automático)

---

¿Necesitas ayuda con algún paso específico? ¡Avísame!
