# 🚨 PROBLEMA IDENTIFICADO: Cloudflare Turnstile

## ❌ Situación Actual
El scraper de ACM está siendo bloqueado por **Cloudflare Turnstile** (CAPTCHA invisible).

```
⚠️  Cloudflare detectado: Just a moment...
❌ Cloudflare no se resolvió automáticamente
```

Esto ocurre porque:
1. ACM usa protección Cloudflare agresiva
2. Tu IP residencial (Mac local) es marcada como sospechosa
3. Playwright en headless es detectado como bot

## ✅ SOLUCIONES (En orden de efectividad)

### 1. ⭐ **SOLUCIÓN RECOMENDADA: Google Cloud VM** (La que usó tu amigo)

**Por qué funciona:**
- IPs de Google Cloud son consideradas confiables
- Servidores en datacenter tienen mejor reputación
- Cloudflare es menos agresivo con IPs empresariales

**Implementación:**
```bash
# 1. Crear VM en Google Cloud
gcloud compute instances create bibliometria-scraper \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --zone=us-central1-a

# 2. Conectar y configurar
gcloud compute ssh bibliometria-scraper
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m playwright install chromium
python3 -m playwright install-deps

# 3. Probar
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1
```

**Costo:** ~$20/mes (o gratis con crédito de $300)

---

### 2. 🔧 **Modo No-Headless** (Temporal, solo local)

Ejecutar con interfaz gráfica y resolver el CAPTCHA manualmente:

```bash
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1 --no-headless
```

**Ventajas:**
- Funciona inmediatamente
- Sin configuración adicional

**Desventajas:**
- Requiere intervención manual
- No se puede automatizar
- Solo funciona en tu Mac (no en servidores)

---

### 3. 🌐 **Proxy Residencial** (Costoso)

Usar servicios como BrightData, Oxylabs, o Smartproxy:

```python
# En acm_scraper_playwright.py
browser = p.chromium.launch(
    proxy={
        "server": "proxy.provider.com:8080",
        "username": "user",
        "password": "pass"
    }
)
```

**Costo:** $50-200/mes

---

### 4. 🕐 **Esperar y Reintentar** (Poco efectivo)

Cloudflare a veces permite acceso después de varios intentos:

```bash
# Modificar el scraper para esperar más tiempo
# Ya implementado en el código con 3 reintentos
```

---

## 🎯 RECOMENDACIÓN INMEDIATA

### Plan A: Usar Google Cloud (2 horas de setup)

1. **Crear cuenta Google Cloud** (te dan $300 de crédito gratis)
   - https://cloud.google.com/free
   
2. **Crear VM Debian** siguiendo `DJANGO_README.md`

3. **Clonar repo y configurar** en la VM

4. **Ejecutar scraper** - debería funcionar sin problemas

### Plan B: Modo No-Headless (5 minutos)

Mientras configuras Google Cloud, puedes scrapear localmente:

```bash
# Terminal 1: Ejecutar con GUI
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1 --no-headless

# Cuando se abra el navegador:
# 1. Resolver el CAPTCHA manualmente
# 2. El scraper continuará automáticamente
```

---

## 📊 Comparación de Soluciones

| Solución | Efectividad | Costo | Setup | Automatizable |
|----------|-------------|-------|-------|---------------|
| Google Cloud VM | ⭐⭐⭐⭐⭐ | $20/mes | 2h | ✅ Sí |
| No-Headless | ⭐⭐⭐ | $0 | 5min | ❌ No |
| Proxy Residencial | ⭐⭐⭐⭐ | $50-200/mes | 1h | ✅ Sí |
| Esperar/Reintentar | ⭐ | $0 | 0 | ❌ No |

---

## 🚀 Próximos Pasos

**Opción 1 (Rápido pero manual):**
```bash
# Probar modo no-headless AHORA
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1 --no-headless
```

**Opción 2 (Correcto y definitivo):**
1. Ir a https://cloud.google.com/free
2. Crear cuenta (requiere tarjeta de crédito pero no cobra si no superas $300)
3. Seguir guía en `DJANGO_README.md` sección "Despliegue en Google Cloud"
4. ¡Scraper funcionará 24/7 sin CAPTCHAs!

---

## 💡 Por qué Google Cloud es la mejor opción

✅ IPs confiables (menos bloqueos)  
✅ Puede correr 24/7  
✅ Automatizable con cron  
✅ Escalable  
✅ Misma solución que funcionó para tu amigo  
✅ $300 de crédito gratis (dura ~15 meses)  

---

**¿Qué prefieres hacer?**
1. Probar modo no-headless ahora (5 min)
2. Configurar Google Cloud (2 horas, solución definitiva)
3. Otra opción
