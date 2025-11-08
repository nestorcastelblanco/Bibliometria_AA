# 🎓 Sistema de Bibliometría con Django + Playwright

## 📋 Descripción

Sistema completo de análisis bibliométrico que combina:
- **Web Scraping** con Playwright (headless, evasión de Cloudflare)
- **API REST** con Django REST Framework
- **Pipeline de Análisis** (similitud, frecuencias, clustering, visualizaciones)
- **Dashboard Web** interactivo

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│  1. SCRAPING (Google Cloud VM)                              │
│     - acm_scraper_playwright.py                             │
│     - Modo headless sin interfaz gráfica                    │
│     - Guarda .bib en data/raw/acm/                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PIPELINE DE ANÁLISIS                                     │
│     - run_all.py (Req2 → Req5)                              │
│     - Genera CSVs, imágenes, PDFs                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. DJANGO REST API + DASHBOARD                              │
│     - Lee archivos .bib y CSVs (sin DB)                    │
│     - API REST para consultas                               │
│     - Dashboard web interactivo                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Instalación Local

### 1. Clonar repositorio
```bash
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
```

### 2. Crear entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o en Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
python3 -m playwright install chromium
python3 -m playwright install-deps  # Dependencias del sistema
```

### 4. Iniciar servidor Django
```bash
python3 manage.py runserver
```

### 5. Abrir Dashboard
Abrir navegador en: **http://127.0.0.1:8000/**

## 📡 API Endpoints

### Papers
- `GET /api/papers/` - Lista todos los papers
- `GET /api/papers/stats/` - Estadísticas generales

### Análisis
- `GET /api/similarity/` - Resultados de similitud textual (Req2)
- `GET /api/frequencies/` - Frecuencias y términos (Req3)
- `GET /api/clusters/` - Clustering jerárquico (Req4)

### Visualizaciones
- `GET /api/visualizations/<filename>` - Imágenes y PDFs

### Triggers (Ejecutar procesos)
- `POST /api/trigger-scrape/` - Iniciar scraping
  ```json
  {
    "pages": 5,
    "headless": true
  }
  ```

- `POST /api/trigger-analysis/` - Iniciar análisis
  ```json
  {
    "req2": [0, 3, 7],
    "req4n": 25
  }
  ```

## 🛠️ Management Commands

### Ejecutar Scraper
```bash
# Scraping básico (2 páginas, headless)
python3 manage.py run_scraper

# Scraping completo (5 páginas)
python3 manage.py run_scraper --pages 5

# Con interfaz gráfica (solo desarrollo local)
python3 manage.py run_scraper --no-headless
```

### Ejecutar Análisis
```bash
# Análisis completo con defaults
python3 manage.py run_analysis

# Análisis personalizado
python3 manage.py run_analysis --req2 0 3 7 --req4n 25 --wcmax 150
```

## 📂 Estructura de Directorios

```
Bibliometria_AA/
├── bibliometria_web/          # Configuración Django
│   ├── settings.py           # Settings con rutas de datos
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI para producción
│
├── api/                       # API REST
│   ├── views.py              # ViewSets (lee archivos)
│   └── urls.py               # Router de endpoints
│
├── scraper_app/               # Gestión de scrapers
│   ├── management/commands/
│   │   ├── run_scraper.py    # Command para scraping
│   │   └── run_analysis.py   # Command para análisis
│   └── views.py              # Dashboard view
│
├── templates/                 # Templates HTML
│   └── dashboard.html        # Dashboard principal
│
├── data/                      # Datos (sin DB)
│   ├── raw/acm/              # .bib descargados
│   └── processed/            # CSVs, imágenes, PDFs
│
├── requirement_1/            # Scrapers
│   └── scrapers/
│       └── acm_scraper_playwright.py
│
├── requirement_2-5/          # Pipeline de análisis
├── run_all.py               # Runner completo
└── requirements.txt         # Dependencias
```

## ☁️ Despliegue en Google Cloud

### 1. Crear VM para Scraping
```bash
# Crear VM Debian 11
gcloud compute instances create bibliometria-scraper \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB

# Conectar a VM
gcloud compute ssh bibliometria-scraper
```

### 2. Configurar VM
```bash
# Instalar dependencias
sudo apt update
sudo apt install -y python3-pip python3-venv git

# Clonar repo
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA

# Configurar entorno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m playwright install chromium
python3 -m playwright install-deps
```

### 3. Probar Scraper en Headless
```bash
python3 requirement_1/scrapers/acm_scraper_playwright.py --pages 1
```

### 4. Configurar Cron (Scraping Automático)
```bash
crontab -e

# Agregar línea (ejecutar cada domingo a las 2 AM)
0 2 * * 0 /home/user/Bibliometria_AA/.venv/bin/python3 /home/user/Bibliometria_AA/requirement_1/scrapers/acm_scraper_playwright.py --pages 5 >> /home/user/scraper.log 2>&1
```

### 5. Desplegar Django en Cloud Run (Opcional)

#### Crear Dockerfile
```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Recolectar archivos estáticos
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

# Ejecutar con gunicorn
CMD ["gunicorn", "bibliometria_web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

#### Desplegar
```bash
# Build y push a Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/bibliometria-api

# Deploy a Cloud Run
gcloud run deploy bibliometria-api \
  --image gcr.io/PROJECT_ID/bibliometria-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔑 Ventajas de Esta Arquitectura

✅ **Sin Base de Datos**: Usa archivos .bib y CSVs  
✅ **Separación de Componentes**: Scraper, Pipeline y API independientes  
✅ **Escalable**: Cada componente puede escalar por separado  
✅ **Probado en Producción**: Misma stack que funcionó en Google Cloud  
✅ **Headless**: Scraper funciona sin interfaz gráfica  

## 📊 Pipeline de Análisis

El pipeline completo ejecuta:

1. **Req2**: Similitud textual entre abstracts
2. **Req3**: Frecuencias y términos asociados
3. **Req4**: Clustering jerárquico + dendrogramas
4. **Req5**: Heatmaps, wordclouds, timelines + PDF

### Ejecutar Pipeline Completo
```bash
python3 run_all.py --req2 0 3 7 --req4n 25 --wcmax 150
```

## 🧪 Testing

### Probar API
```bash
# Stats de papers
curl http://127.0.0.1:8000/api/papers/stats/

# Trigger scraping
curl -X POST http://127.0.0.1:8000/api/trigger-scrape/ \
  -H "Content-Type: application/json" \
  -d '{"pages": 2, "headless": true}'

# Trigger análisis
curl -X POST http://127.0.0.1:8000/api/trigger-analysis/ \
  -H "Content-Type: application/json" \
  -d '{"req2": [0,3,7], "req4n": 25}'
```

## 📝 Notas Importantes

- **NO usar en producción** con `DEBUG=True`
- **Configurar SECRET_KEY** en producción
- **Usar HTTPS** en producción
- **Configurar ALLOWED_HOSTS** correctamente
- **Limitar rate de scraping** para no ser bloqueado

## 🤝 Créditos

Basado en la solución exitosa de Juan David Guzmán:
- Django como framework
- Google Cloud VM (Debian sin GUI)
- Playwright en modo headless

## 📄 Licencia

MIT License
