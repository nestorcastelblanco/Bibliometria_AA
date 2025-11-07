# 🚨 ERRORES COMUNES al desplegar en AWS

## Resumen Ejecutivo

**TU MAYOR DESAFÍO**: Selenium + Chrome en AWS

### ¿Por qué tu .venv NO debe ir a AWS?

1. **Específico de tu máquina**: Contiene paths absolutos de tu Mac
2. **Ocupa mucho espacio**: Cientos de MB innecesarios
3. **Incompatibilidad de arquitectura**: Binarios compilados para macOS no funcionan en Linux
4. **Ya está en .gitignore**: Git lo ignora automáticamente

### Errores que SEGURO tendrás:

## 1. ❌ Chrome/ChromeDriver no encontrado

**Error típico:**
```
selenium.common.exceptions.WebDriverException: 
Message: 'chromedriver' executable needs to be in PATH
```

**Causa:** AWS EC2 no tiene Chrome instalado por defecto

**Solución:**
```bash
# En EC2, ejecutar:
chmod +x install_chrome_ec2.sh
./install_chrome_ec2.sh
```

## 2. ❌ Display :0 not found

**Error típico:**
```
selenium.common.exceptions.WebDriverException: 
Message: unknown error: Chrome failed to start: exited abnormally
  (Driver info: chromedriver=... chrome=...)
```

**Causa:** Chrome intenta abrir ventana gráfica pero EC2 no tiene GUI

**Solución:** Tu código ya está preparado con modo headless automático
```python
# Esto ya está en tus scrapers:
if IS_PRODUCTION:
    options.add_argument('--headless=new')
```

## 3. ❌ Memory errors / Out of RAM

**Error típico:**
```
selenium.common.exceptions.WebDriverException: 
Message: unknown error: session deleted because of page crash
```

**Causa:** Chrome consume mucha RAM (especialmente con múltiples pestañas)

**Solución:** Usar instancia con >= 4GB RAM (t3.medium o superior)

```bash
# Agregar swap si es necesario
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 4. ❌ Timeouts muy cortos

**Error típico:**
```
requests.exceptions.ReadTimeout: HTTPConnectionPool...
```

**Causa:** Scrapers tardan 10-15 minutos, Gunicorn timeout por defecto es 30s

**Solución:** Ya configurado en Procfile
```bash
gunicorn webui:app --timeout 600  # 10 minutos
```

## 5. ❌ Permisos de descarga

**Error típico:**
```
PermissionError: [Errno 13] Permission denied: '/app/data/raw/acm'
```

**Solución:**
```bash
# Dar permisos correctos
sudo chown -R ubuntu:ubuntu ~/Bibliometria_AA
chmod -R 755 ~/Bibliometria_AA/data
```

## 6. ❌ Puerto ocupado / no accesible

**Error típico:**
```
curl: (7) Failed to connect to xxx.xxx.xxx.xxx port 8080: Connection refused
```

**Causa:** Security Group no permite tráfico al puerto

**Solución:** En AWS Console > EC2 > Security Groups
```
Inbound Rules:
- Type: Custom TCP
- Port: 8080
- Source: 0.0.0.0/0 (o tu IP)
```

## 7. ❌ ModuleNotFoundError en producción

**Error típico:**
```
ModuleNotFoundError: No module named 'undetected_chromedriver'
```

**Causa:** Dependencias no instaladas correctamente

**Solución:**
```bash
source venv/bin/activate
pip install -r requirements-production.txt
```

## 8. ❌ CAPTCHA sigue apareciendo

**Error típico:**
Scraper se queda esperando indefinidamente

**Causa:** IP de AWS puede estar bloqueada, o headless mal configurado

**Solución:**
```python
# Verificar que headless usa user-agent realista
options.add_argument('--user-agent=Mozilla/5.0...')
```

## 9. ❌ Archivos no se descargan

**Error típico:**
Los scrapers terminan pero no hay archivos .bib

**Causa:** Directorio de descargas no existe o permisos incorrectos

**Solución:**
```bash
mkdir -p data/raw/acm data/raw/sage
chmod 755 data/raw/acm data/raw/sage
```

## 10. ❌ Proceso zombie / Chrome no cierra

**Error típico:**
```bash
ps aux | grep chrome
# Muestra muchos procesos chrome colgados
```

**Causa:** driver.quit() no se ejecuta correctamente

**Solución:** Tus scrapers ya tienen manejo correcto:
```python
finally:
    driver.quit()
```

Si persiste:
```bash
# Matar todos los procesos Chrome
pkill -9 chrome
pkill -9 chromedriver
```

---

## Checklist Pre-Despliegue

Antes de subir a AWS, verifica:

- [ ] `.venv/` está en `.gitignore` ✅ (ya configurado)
- [ ] `requirements-production.txt` tiene todas las dependencias ✅
- [ ] Scrapers detectan modo producción y usan headless ✅
- [ ] webui.py usa host 0.0.0.0 en producción ✅
- [ ] Tienes script `install_chrome_ec2.sh` ✅
- [ ] Security Group permite puerto 8080
- [ ] Instancia EC2 tiene >= 4GB RAM (t3.medium)
- [ ] Has probado localmente: `bash test_production.sh`

---

## Workflow Recomendado

```bash
# 1. LOCAL: Probar que todo funciona
bash test_production.sh

# 2. LOCAL: Commit y push
git add .
git commit -m "Preparar para AWS"
git push origin deployment

# 3. EC2: Conectar por SSH
ssh -i key.pem ubuntu@tu-ip

# 4. EC2: Clonar y setup
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
./install_chrome_ec2.sh
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt

# 5. EC2: Probar manualmente primero
ENVIRONMENT=production python webui.py
# Abrir en navegador: http://ip:8080
# Probar Req1

# 6. EC2: Si funciona, configurar como servicio
sudo cp bibliometria.service /etc/systemd/system/
sudo systemctl start bibliometria
sudo systemctl enable bibliometria
```

---

## 🆘 Debugging Avanzado

### Ver logs en tiempo real

```bash
# Logs de aplicación
tail -f ~/Bibliometria_AA/*.log

# Logs de systemd
sudo journalctl -u bibliometria -f

# Logs de sistema
dmesg | tail -50
```

### Probar Chrome manualmente

```bash
google-chrome --version
google-chrome --headless --dump-dom https://www.google.com
```

### Verificar puertos

```bash
sudo netstat -tulpn | grep :8080
curl -v http://localhost:8080
```

### Verificar memoria

```bash
free -h
df -h
ps aux --sort=-%mem | head
```

---

¿Tienes algún error específico? Compártelo y te ayudo a resolverlo.
