# 🚀 GUÍA PASO A PASO: Google Cloud Setup

## 📋 CHECKLIST DE SETUP

### FASE 1: Crear Cuenta Google Cloud (10 minutos)
- [ ] Ir a https://cloud.google.com/free
- [ ] Crear cuenta con tu Gmail
- [ ] Verificar con tarjeta de crédito (no te cobrarán)
- [ ] Activar crédito de $300 USD gratis
- [ ] Aceptar términos y condiciones

### FASE 2: Crear VM para Scraping (15 minutos)
- [ ] Abrir Google Cloud Console
- [ ] Ir a "Compute Engine" → "VM instances"
- [ ] Crear nueva instancia
- [ ] Configurar según especificaciones
- [ ] Iniciar VM

### FASE 3: Configurar VM (30 minutos)
- [ ] Conectar por SSH
- [ ] Instalar Python y dependencias
- [ ] Instalar Playwright
- [ ] Clonar repositorio
- [ ] Configurar entorno virtual

### FASE 4: Probar Scraper (10 minutos)
- [ ] Ejecutar scraper de prueba
- [ ] Verificar que no hay bloqueo de Cloudflare
- [ ] Revisar archivos .bib descargados

### FASE 5: Automatizar con Cron (10 minutos)
- [ ] Configurar cron job
- [ ] Probar ejecución automática
- [ ] Configurar notificaciones (opcional)

---

## 🎯 FASE 1: CREAR CUENTA GOOGLE CLOUD

### Paso 1.1: Registrarse

1. **Abre tu navegador** y ve a:
   ```
   https://cloud.google.com/free
   ```

2. **Haz clic en "Empezar gratis"** o "Get started for free"

3. **Inicia sesión** con tu cuenta de Gmail

4. **Completa el formulario:**
   - País: Colombia (o tu país)
   - Tipo de cuenta: Individual
   - Términos: Acepta los términos

5. **Verificación de pago:**
   - Agrega una tarjeta de crédito o débito
   - **IMPORTANTE:** No te cobrarán automáticamente
   - Solo es para verificar tu identidad
   - Recibes $300 USD de crédito gratis

6. **¡Listo!** Ahora tienes acceso a Google Cloud Console

---

## 🖥️ FASE 2: CREAR VM PARA SCRAPING

### Paso 2.1: Acceder a Compute Engine

1. En Google Cloud Console, busca "Compute Engine" en el buscador superior
2. Haz clic en **"VM instances"**
3. Si es tu primera vez, espera a que se inicialice (1-2 minutos)

### Paso 2.2: Crear VM

Haz clic en **"CREATE INSTANCE"** y configura:

#### **Configuración Básica:**
```
Name: bibliometria-scraper
Region: us-central1 (Iowa) - Más barato
Zone: us-central1-a
```

#### **Machine Configuration:**
```
Series: E2
Machine type: e2-medium
  - 2 vCPU
  - 4 GB memory
  - Costo: ~$24/mes (con crédito gratis no pagas)
```

#### **Boot Disk:**
Haz clic en "CHANGE" y selecciona:
```
Operating System: Debian
Version: Debian GNU/Linux 11 (bullseye)
Boot disk type: Standard persistent disk
Size: 20 GB
```

#### **Firewall:**
```
☑️ Allow HTTP traffic
☑️ Allow HTTPS traffic
```

### Paso 2.3: Crear la VM

1. Haz clic en **"CREATE"** (abajo)
2. Espera 1-2 minutos a que se cree
3. Verás tu VM en la lista con un ✅ verde

---

## 🔧 FASE 3: CONFIGURAR VM

### Paso 3.1: Conectar por SSH

En la lista de VMs, haz clic en **"SSH"** al lado de tu VM.

Se abrirá una terminal en tu navegador. ¡Ya estás dentro de la VM!

### Paso 3.2: Instalar Dependencias del Sistema

Copia y pega estos comandos uno por uno:

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y git python3 python3-pip python3-venv curl wget

# Verificar instalación
python3 --version  # Debe mostrar Python 3.9+
git --version
```

### Paso 3.3: Clonar Repositorio

```bash
# Ir a directorio home
cd ~

# Clonar tu repo
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git

# Entrar al directorio
cd Bibliometria_AA

# Ver archivos
ls -la
```

### Paso 3.4: Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Deberías ver (.venv) al inicio de tu prompt
```

### Paso 3.5: Instalar Dependencias Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Esto tardará 2-3 minutos
```

### Paso 3.6: Instalar Playwright

```bash
# Instalar Playwright
python3 -m playwright install chromium

# Instalar dependencias del sistema para Playwright
python3 -m playwright install-deps

# Esto tardará 3-5 minutos y pedirá contraseña
# La contraseña es tu password de Google (el que usas en Gmail)
```

---

## 🧪 FASE 4: PROBAR SCRAPER

### Paso 4.1: Probar Scraper (1 página)

```bash
# Asegúrate de estar en el directorio correcto
cd ~/Bibliometria_AA

# Activar entorno virtual si no está activo
source .venv/bin/activate

# Ejecutar scraper de prueba
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1
```

**¡ESTE ES EL MOMENTO CRÍTICO!**

Si ves:
```
✅ Página cargada: Search Results – ACM Digital Library
☑️ Seleccionando resultados...
✅ Resultados seleccionados: 50
```

**¡ÉXITO! 🎉** Cloudflare no te está bloqueando.

Si ves:
```
⚠️ Cloudflare detectado: Just a moment...
```

Espera 20 segundos y prueba de nuevo. Las IPs de Google Cloud son más confiables.

### Paso 4.2: Verificar Archivos Descargados

```bash
# Ver archivos descargados
ls -lh ~/Bibliometria_AA/data/raw/acm/

# Contar archivos .bib
ls ~/Bibliometria_AA/data/raw/acm/*.bib | wc -l

# Ver contenido del último archivo
ls -t ~/Bibliometria_AA/data/raw/acm/*.bib | head -1 | xargs head -20
```

### Paso 4.3: Probar Scraping Completo (5 páginas)

Si el test funcionó, prueba con más páginas:

```bash
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 5
```

Esto tardará 5-10 minutos.

---

## ⏰ FASE 5: AUTOMATIZAR CON CRON

### Paso 5.1: Crear Script de Scraping

```bash
# Crear script ejecutable
nano ~/scrape_acm.sh
```

Pega este contenido:

```bash
#!/bin/bash
# Script para ejecutar scraping automático

# Activar entorno virtual
source /home/$(whoami)/Bibliometria_AA/.venv/bin/activate

# Ir al directorio del proyecto
cd /home/$(whoami)/Bibliometria_AA

# Ejecutar scraper
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 5 >> /home/$(whoami)/scraper.log 2>&1

# Sincronizar archivos (si usas Cloud Storage)
# gsutil rsync -r data/raw/acm/ gs://tu-bucket/acm/

echo "Scraping completado: $(date)" >> /home/$(whoami)/scraper.log
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Dar permisos de ejecución
chmod +x ~/scrape_acm.sh

# Probar script
~/scrape_acm.sh
```

### Paso 5.2: Configurar Cron Job

```bash
# Abrir crontab
crontab -e

# Si pregunta por editor, selecciona nano (opción 1)
```

Agrega esta línea al final:

```bash
# Ejecutar cada domingo a las 2 AM
0 2 * * 0 /home/$(whoami)/scrape_acm.sh
```

**Otras opciones de frecuencia:**
```bash
# Cada día a las 3 AM
0 3 * * * /home/$(whoami)/scrape_acm.sh

# Cada lunes a las 8 AM
0 8 * * 1 /home/$(whoami)/scrape_acm.sh

# Cada 12 horas
0 */12 * * * /home/$(whoami)/scrape_acm.sh
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

### Paso 5.3: Verificar Cron

```bash
# Ver cron jobs configurados
crontab -l

# Ver logs de cron
sudo tail -f /var/log/syslog | grep CRON
```

---

## 📊 MONITOREO Y MANTENIMIENTO

### Ver Logs del Scraper

```bash
# Ver últimas 50 líneas
tail -50 ~/scraper.log

# Ver en tiempo real
tail -f ~/scraper.log

# Buscar errores
grep -i error ~/scraper.log
```

### Revisar Archivos Descargados

```bash
# Contar papers
ls ~/Bibliometria_AA/data/raw/acm/*.bib | wc -l

# Ver último archivo
ls -t ~/Bibliometria_AA/data/raw/acm/*.bib | head -1 | xargs ls -lh

# Espacio usado
du -sh ~/Bibliometria_AA/data/
```

### Descargar Archivos a tu Mac

Desde tu terminal local (Mac):

```bash
# Usando gcloud
gcloud compute scp \
  bibliometria-scraper:~/Bibliometria_AA/data/raw/acm/*.bib \
  ~/Documents/GitHub/Bibliometria_AA/data/raw/acm/ \
  --zone=us-central1-a

# O descargar directamente desde la consola SSH
# Haz clic derecho en los archivos y "Download"
```

---

## 💰 COSTOS ESTIMADOS

### VM e2-medium (2 vCPU, 4 GB RAM)
```
Costo mensual: ~$24 USD
Con crédito de $300: GRATIS por ~12 meses
Después del crédito: $24/mes
```

### Storage (20 GB disco)
```
Costo mensual: ~$0.80 USD
Con crédito: GRATIS
```

### Egress (descarga de datos)
```
Primer GB al mes: GRATIS
Después: $0.12/GB
```

**Total estimado:** $25/mes después del crédito de $300

### Cómo Ahorrar:
- Apagar VM cuando no la uses: `$0`
- Usar VM e2-micro (0.25 GB): `$7/mes`
- Ejecutar solo 1 vez por semana: Mismo costo

---

## 🚨 TROUBLESHOOTING

### Error: "Permission denied"
```bash
sudo chmod +x ~/scrape_acm.sh
```

### Error: "playwright not found"
```bash
source .venv/bin/activate
python3 -m playwright install chromium
```

### Cloudflare sigue bloqueando
```bash
# Cambiar región de la VM
# Crear nueva VM en europe-west1 o asia-southeast1
# IPs de diferentes regiones tienen diferentes reputaciones
```

### VM muy lenta
```bash
# Upgrade a e2-standard-2 (2 vCPU, 8 GB)
# Costo: ~$50/mes
```

---

## ✅ CHECKLIST FINAL

Antes de terminar, verifica:

- [ ] VM está corriendo (luz verde en Console)
- [ ] SSH funciona
- [ ] Python y Playwright instalados
- [ ] Scraper de prueba funcionó (1 página)
- [ ] Archivos .bib se crearon
- [ ] Cron job configurado
- [ ] Script de backup funciona

---

## 📞 SOPORTE

Si algo falla:
1. Revisa logs: `cat ~/scraper.log`
2. Prueba manualmente: `python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1`
3. Verifica Playwright: `python3 -m playwright --version`
4. Revisa el archivo `CLOUDFLARE_PROBLEMA.md`

---

**¡Empecemos! Dime cuando estés listo y te ayudo con cada paso.**
