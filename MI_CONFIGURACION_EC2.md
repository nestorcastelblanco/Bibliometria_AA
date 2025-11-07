# 🚀 CONFIGURACIÓN DE TU INSTANCIA EC2 - Bibliometria

## ✅ Configuración Seleccionada

### 📋 Detalles de la Instancia

| Parámetro | Valor Seleccionado |
|-----------|-------------------|
| **Nombre** | Bibliometria |
| **AMI** | Ubuntu Server 24.04 LTS (ami-077aec33f15de0896) |
| **Arquitectura** | 64 bits (x86) |
| **Tipo de Instancia** | **t3.small** |
| **vCPUs** | 2 |
| **Memoria RAM** | 2 GB |
| **Par de Claves** | biblio.pem |
| **Storage** | 15 GB (gp3) |
| **Región** | sa-east-1 (São Paulo) |

### 💰 Costo Estimado

```
EC2 t3.small:      ~$15/mes  (2 vCPUs, 2 GB RAM)
Storage 15 GB:     ~$1.50/mes
Elastic IP:        ~$3.60/mes (si se asigna)
────────────────────────────────────────
TOTAL:             ~$20/mes
```

### 🔒 Security Group Configurado

✅ **Reglas de entrada actuales:**
- SSH (22): Habilitado
- HTTPS (443): Habilitado  
- HTTP (80): Habilitado

⚠️ **IMPORTANTE - Agregar después de lanzar:**
- **Custom TCP (8080)**: REQUERIDO para la aplicación
  - Puerto: 8080
  - Origen: 0.0.0.0/0 (o tu IP específica)

---

## 🎯 PRÓXIMOS PASOS (Después de Lanzar)

### 1️⃣ Obtener IP Pública

Una vez que la instancia esté **"Running"**:
1. Ir a EC2 > Instancias
2. Seleccionar "Bibliometria"
3. Copiar la **IPv4 pública** (ejemplo: 18.xxx.xxx.xxx)

### 2️⃣ Conectar por SSH

```bash
# En tu Mac Terminal
cd ~/Downloads
chmod 400 biblio.pem
ssh -i biblio.pem ubuntu@TU-IP-PUBLICA
```

Ejemplo:
```bash
ssh -i biblio.pem ubuntu@18.231.123.456
```

### 3️⃣ Setup Inicial en EC2

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11, pip y git
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Verificar instalación
python3.11 --version
git --version
```

### 4️⃣ Clonar Repositorio

```bash
# Clonar tu proyecto
cd ~
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
```

### 5️⃣ Instalar Chrome (CRÍTICO)

```bash
# Dar permisos y ejecutar script
chmod +x install_chrome_ec2.sh
./install_chrome_ec2.sh

# Verificar instalación
google-chrome --version
```

Deberías ver algo como: `Google Chrome 130.0.6723.58`

### 6️⃣ Setup Python y Dependencias

```bash
# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias (toma ~2-3 minutos)
pip install -r requirements-production.txt

# Verificar instalaciones críticas
python -c "import undetected_chromedriver; print('✅ UC:', undetected_chromedriver.__version__)"
python -c "import flask; print('✅ Flask OK')"
python -c "import selenium; print('✅ Selenium OK')"
```

### 7️⃣ Crear Directorios de Datos

```bash
# Crear estructura de carpetas
mkdir -p data/raw/acm
mkdir -p data/raw/sage
mkdir -p data/processed

# Verificar
ls -la data/
```

### 8️⃣ Configurar Puerto 8080 en Security Group

**Mientras instala las dependencias, haz esto en la consola AWS:**

1. EC2 > Instancias > Bibliometria
2. Pestaña **"Seguridad"**
3. Click en el **Security Group** (sg-xxxxx)
4. **"Editar reglas de entrada"**
5. **"Agregar regla"**:
   - Tipo: **TCP personalizado**
   - Puerto: **8080**
   - Origen: **0.0.0.0/0** (o "Mi IP" si prefieres más seguridad)
6. **"Guardar reglas"**

### 9️⃣ Ejecutar Aplicación

```bash
# En EC2, dentro de ~/Bibliometria_AA con venv activado
export ENVIRONMENT=production
export PORT=8080
python webui.py
```

Deberías ver:
```
🚀 Modo PRODUCCIÓN - Servidor en 0.0.0.0:8080
 * Running on http://0.0.0.0:8080
```

### 🔟 Probar en el Navegador

```
http://TU-IP-PUBLICA:8080
```

Ejemplo: `http://18.231.123.456:8080`

---

## ✅ Checklist de Verificación

Marca cuando completes cada paso:

- [ ] Instancia EC2 "Running"
- [ ] IP pública obtenida
- [ ] SSH conectado exitosamente
- [ ] Python 3.11 instalado
- [ ] Repositorio clonado
- [ ] Chrome instalado y verificado
- [ ] venv creado
- [ ] Dependencias instaladas
- [ ] Directorios de datos creados
- [ ] Puerto 8080 abierto en Security Group
- [ ] Aplicación ejecutándose
- [ ] Acceso web funcionando

---

## 🎓 Para la Demostración al Profesor

### Puntos a Destacar:

1. **Anti-CAPTCHA**: Los scrapers usan `undetected-chromedriver`
   - ACM Digital Library: ✅ Sin CAPTCHA
   - SAGE Journals: ✅ Bypass de Cloudflare

2. **Modo Headless**: Chrome corre sin interfaz gráfica
   ```bash
   # Verificar que está en headless
   ps aux | grep chrome
   ```

3. **Producción Ready**: 
   - Gunicorn como servidor WSGI
   - Timeout de 600s para scrapers largos
   - Flask en modo producción

4. **Testing Rápido**: Scrapers limitados a 2 páginas
   - ACM: ~2 minutos
   - SAGE: ~3 minutos
   - Total: ~5 minutos de scraping

### Flujo de Demo:

1. Abrir `http://IP:8080`
2. Click en **"Ejecutar Req1"**
3. Mostrar que Chrome ejecuta en headless (terminal)
4. Esperar ~5 minutos
5. Ver archivos descargados: `ls data/raw/acm/ data/raw/sage/`
6. Ver gráficos generados en la interfaz web

---

## 🆘 Troubleshooting Rápido

### Chrome no se instala
```bash
# Reinstalar manualmente
sudo apt update
sudo apt install -y wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
```

### Puerto 8080 no accesible
- Verificar Security Group tiene regla para puerto 8080
- Verificar que Flask esté corriendo: `ps aux | grep python`

### Error de memoria (poco probable con t3.small)
```bash
# Verificar memoria disponible
free -h

# Si necesitas, agregar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📊 Especificaciones Técnicas (Para el Reporte)

### Infraestructura
- **Cloud Provider**: AWS (Amazon Web Services)
- **Servicio**: EC2 (Elastic Compute Cloud)
- **Región**: sa-east-1 (São Paulo, Brasil)
- **Disponibilidad**: 99.99% SLA

### Servidor
- **OS**: Ubuntu Server 24.04 LTS
- **Compute**: 2 vCPUs (Intel Xeon)
- **RAM**: 2 GB DDR4
- **Storage**: 15 GB SSD (gp3)
- **Network**: Enhanced Networking

### Stack Tecnológico
- **Python**: 3.11
- **Web Server**: Gunicorn (WSGI)
- **Framework**: Flask 3.1
- **Scraping**: Selenium 4.15 + undetected-chromedriver 3.5
- **Browser**: Google Chrome (headless mode)

### Performance
- **Startup Time**: ~30 segundos
- **Scraping Time**: ~5 minutos (2 páginas c/u)
- **Concurrent Users**: 2 (configurado con 2 workers)
- **Request Timeout**: 600 segundos

---

**Guardado el:** 7 de noviembre de 2025  
**IP de la instancia:** _(agregar cuando esté running)_  
**Estado:** Listo para desplegar ✅
