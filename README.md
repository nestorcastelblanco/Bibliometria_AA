# 📚 Sistema de Análisis Bibliométrico y Algoritmos de Ordenamiento

**Proyecto Académico de Análisis Bibliométrico Automatizado**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Requisitos del Sistema](#-requisitos-del-sistema)
5. [Instalación](#-instalación)
6. [Requerimientos Funcionales](#-requerimientos-funcionales)
7. [Uso del Sistema](#-uso-del-sistema)
8. [Interfaz Web](#-interfaz-web)
9. [Metodología Científica](#-metodología-científica)
10. [Resultados y Outputs](#-resultados-y-outputs)
11. [Troubleshooting](#-troubleshooting)
12. [Contribuciones](#-contribuciones)

---

## 🎯 Descripción General

Este proyecto implementa un **sistema completo de análisis bibliométrico** que combina:

1. **Web Scraping Automatizado**: Extracción de artículos académicos desde bases de datos científicas (ACM Digital Library, SAGE Journals)
2. **Análisis de Algoritmos de Ordenamiento**: Implementación y comparación de 12 algoritmos de ordenamiento sobre datos bibliográficos
3. **Análisis de Similitud Textual**: Comparación de abstracts usando técnicas NLP clásicas y modelos de IA
4. **Análisis de Frecuencia**: Extracción automática de términos relevantes usando TF-IDF
5. **Clustering Jerárquico**: Agrupamiento de documentos por similitud semántica
6. **Visualizaciones Avanzadas**: Mapas de calor geográficos, nubes de palabras, líneas temporales

### 🎓 Contexto Académico

El proyecto fue diseñado para satisfacer los requisitos de un curso de **Estructuras de Datos y Algoritmos**, demostrando:
- Implementación práctica de algoritmos de ordenamiento
- Análisis de complejidad temporal y espacial
- Aplicación de estructuras de datos (árboles, heaps, buckets)
- Procesamiento de grandes volúmenes de datos bibliográficos
- Visualización de resultados científicos

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ DE USUARIO                      │
│  ┌─────────────────┐         ┌────────────────────────┐     │
│  │   CLI (main.py) │         │  Web UI (webui.py)     │     │
│  │   run_all.py    │         │  Flask Server          │     │
│  └─────────────────┘         └────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                      CAPA DE LÓGICA                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Requirement │  │  Requirement │  │  Requirement │         │
│  │      1       │  │      2       │  │      3       │         │
│  │  (Scraping)  │  │ (Similarity) │  │ (Frequency)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Requirement │  │  Requirement │  │ Seguimiento  │         │
│  │      4       │  │      5       │  │      1       │         │
│  │ (Clustering) │  │(Visualizat.) │  │ (Sorting)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                     CAPA DE DATOS                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐            │
│  │  Raw Data  │  │  Processed  │  │   Outputs    │            │
│  │  (BibTeX)  │  │    Data     │  │  (CSV/JSON)  │            │
│  │  data/raw/ │  │data/process/│  │data/process/ │            │
│  └────────────┘  └─────────────┘  └──────────────┘            │
└───────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
Bibliometria_AA/
│
├── 📄 main.py                    # Punto de entrada CLI principal
├── 📄 run_all.py                 # Ejecutor secuencial de todos los requerimientos
├── 📄 webui.py                   # Interfaz web Flask
├── 📄 requirements.txt           # Dependencias Python
├── 📄 .gitignore                 # Archivos excluidos de Git
│
├── 📁 requirement_1/             # REQUERIMIENTO 1: Web Scraping
│   ├── 📁 scrapers/
│   │   ├── acm_scraper.py       # Scraper para ACM Digital Library
│   │   └── sage_scraper.py      # Scraper para SAGE Journals
│   └── unificar.py              # Unificador de archivos BibTeX
│
├── 📁 requirement_2/             # REQUERIMIENTO 2: Similitud Textual
│   ├── run_similarity.py        # Ejecutor principal
│   ├── classic.py               # Algoritmos clásicos (TF-IDF, LSA, LDA)
│   ├── ai_models.py             # Modelos embeddings (SentenceTransformer)
│   ├── preprocessing.py         # Limpieza y normalización de texto
│   ├── reports.py               # Generación de reportes Markdown/CSV
│   └── console_report.py        # Resumen en consola
│
├── 📁 requirement_3/             # REQUERIMIENTO 3: Frecuencia y Términos
│   ├── run_req3.py              # Pipeline principal
│   ├── frequency.py             # Cálculo de frecuencias
│   ├── auto_terms.py            # Extracción automática (TF-IDF)
│   ├── evaluate.py              # Evaluación de precisión
│   ├── keywords.py              # Términos semilla
│   └── data_loader.py           # Carga de datos BibTeX
│
├── 📁 requirement_4/             # REQUERIMIENTO 4: Clustering
│   ├── run_req4.py              # Ejecutor principal
│   ├── clustering.py            # Algoritmos jerárquicos
│   └── dendrograms.py           # Visualización de dendrogramas
│
├── 📁 requirement_5/             # REQUERIMIENTO 5: Visualizaciones
│   ├── run_req5.py              # Pipeline visual completo
│   ├── geo.py                   # Mapas de calor geográficos
│   ├── wordcloud_gen.py         # Nubes de palabras
│   ├── timeline.py              # Líneas temporales
│   └── data_loader5.py          # Cargador de datos
│
├── 📁 Seguimiento_1/             # SEGUIMIENTO 1: Algoritmos de Ordenamiento
│   ├── algoritmos_ordenamiento.py    # Ejecutor de todos los algoritmos
│   ├── author_range.py               # Análisis por rango de autores
│   └── stats_algoritmos.py           # Estadísticas y gráficos
│
├── 📁 data/                      # DIRECTORIO DE DATOS
│   ├── 📁 raw/                   # Datos crudos descargados
│   │   ├── acm/                 # BibTeX de ACM
│   │   └── sage/                # BibTeX de SAGE
│   └── 📁 processed/             # Datos procesados
│       ├── productos_unificados.bib    # BibTeX unificado
│       ├── ordenamiento/               # Archivos ordenados
│       └── algoritmos_ordenamiento/    # Scripts de ordenamiento
│           ├── timsort.py
│           ├── quicksort.py
│           ├── heap_sort.py
│           ├── radix_sort.py
│           ├── bucket_sort.py
│           ├── comb_sort.py
│           ├── binary_insertion.py
│           ├── bitonic_sort.py
│           ├── selection_sort.py
│           ├── gnome_sort.py
│           ├── pigeonhole.py
│           └── treesort.py
│
├── 📁 templates/                 # Plantillas HTML (Flask)
│   └── index.html               # Interfaz web principal
│
└── 📁 utils/                     # Utilidades compartidas
    └── helpers.py               # Funciones auxiliares
```

---

## 💻 Requisitos del Sistema

### Requisitos de Hardware

- **CPU**: Procesador multi-core (recomendado: 4+ cores)
- **RAM**: Mínimo 8 GB (recomendado: 16 GB para análisis grandes)
- **Almacenamiento**: 2 GB de espacio libre
- **Internet**: Conexión estable para web scraping

### Requisitos de Software

```yaml
Sistema Operativo:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+)

Python:
  - Versión: 3.8 o superior
  - pip: Última versión

Navegador (para scraping):
  - Google Chrome: Última versión
  - ChromeDriver: Compatible con Chrome
```

### Dependencias Python

```txt
# Web Scraping
selenium==4.15.0
undetected-chromedriver==3.5.4
webdriver-manager==4.0.1
beautifulsoup4==4.12.2
requests==2.31.0

# Procesamiento de Datos
pandas==2.1.3
numpy==1.24.3
bibtexparser==1.4.0

# NLP y Machine Learning
scikit-learn==1.3.2
sentence-transformers==2.2.2
transformers==4.35.2
torch==2.1.1
nltk==3.8.1
gensim==4.3.2

# Visualización
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0
wordcloud==1.9.3
kaleido==0.2.1

# Geografía
pycountry==23.12.11

# Web Framework
flask==3.0.0

# Utilidades
tqdm==4.66.1
openpyxl==3.1.2
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
# Clonar desde GitHub
git clone https://github.com/nestorcastelblanco/Bibliometria_AA.git
cd Bibliometria_AA
```

### 2. Crear Entorno Virtual

#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### En macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt

# Descargar recursos NLTK (requerido)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 4. Configurar ChromeDriver (para scraping)

El sistema usa `undetected-chromedriver` que gestiona ChromeDriver automáticamente.
**No es necesario instalar ChromeDriver manualmente.**

Asegúrate de tener Google Chrome instalado en tu sistema.

### 5. Verificar Instalación

```bash
# Verificar versión de Python
python --version  # Debe ser 3.8+

# Verificar que todas las dependencias se instalaron
pip list

# Prueba rápida
python main.py --help
```

---

## 🔧 Requerimientos Funcionales

### 📊 Requerimiento 1: Web Scraping Automatizado

**Objetivo**: Extraer artículos académicos de bases de datos científicas.

#### Características:
- ✅ Scraping de ACM Digital Library
- ✅ Scraping de SAGE Journals
- ✅ Navegación automática por páginas de resultados
- ✅ Selección masiva de artículos
- ✅ Exportación a formato BibTeX
- ✅ Manejo de sesiones autenticadas
- ✅ Modo headless (sin interfaz gráfica)

#### Tecnologías:
- **Selenium** con `undetected-chromedriver` (evita detección de bots)
- **BeautifulSoup4** para parsing HTML
- **Requests** para descargas HTTP

#### Outputs:
```
data/raw/acm/
  └── articulos_acm_YYYYMMDD_HHMMSS.bib
data/raw/sage/
  └── articulos_sage_YYYYMMDD_HHMMSS.bib
data/processed/
  └── productos_unificados.bib  # Archivo consolidado
```

---

### 🔀 Seguimiento 1: Algoritmos de Ordenamiento

**Objetivo**: Implementar y comparar 12 algoritmos de ordenamiento sobre datos bibliográficos.

#### Algoritmos Implementados:

| Algoritmo | Complejidad (Promedio) | Complejidad (Peor) | Estable | Tiempo Medido |
|-----------|------------------------|-------------------|---------|---------------|
| **TimSort** | O(n log n) | O(n log n) | ✅ | 0.007775 s |
| **QuickSort** | O(n log n) | O(n²) | ❌ | 0.015041 s |
| **Gnome Sort** | O(n²) | O(n²) | ✅ | 0.032919 s |
| **Tree Sort** | O(n log n) | O(n²) | ✅ | 0.082040 s |
| **Comb Sort** | O(n²/2ᵖ) | O(n²) | ❌ | 0.089920 s |
| **Binary Insertion** | O(n²) | O(n²) | ✅ | 0.092856 s |
| **Pigeonhole Sort** | O(n + N) | O(n + N) | ✅ | 0.182685 s |
| **Bucket Sort** | O(n + k) | O(n²) | ✅ | 0.225239 s |
| **Bitonic Sort** | O(log² n) | O(log² n) | ❌ | 0.360274 s |
| **Heap Sort** | O(n log n) | O(n log n) | ❌ | 1.478462 s |
| **Radix Sort** | O(d × n) | O(d × n) | ✅ | 2.360685 s |
| **Selection Sort** | O(n²) | O(n²) | ❌ | 8.256235 s |

#### Criterios de Ordenamiento:
1. **Primario**: Año de publicación (ascendente)
2. **Secundario**: Título (alfabético)

#### Características:
- ✅ Implementación desde cero (sin `sorted()` nativo)
- ✅ Medición precisa de tiempos de ejecución
- ✅ Manejo de campos faltantes o inválidos
- ✅ Normalización de texto (lowercase, sin acentos)
- ✅ Estadísticas comparativas con gráficos

#### Outputs:
```
data/processed/ordenamiento/
  ├── ordenado_timsort.bib
  ├── ordenado_quicksort.bib
  ├── ordenado_heap.bib
  └── ... (12 archivos)
Seguimiento_1/
  └── comparacion_algoritmos.png  # Gráfico de barras
```

---

### 🧬 Requerimiento 2: Similitud Textual

**Objetivo**: Comparar abstracts de artículos usando múltiples técnicas NLP.

#### Algoritmos Implementados:

**Clásicos (sin IA):**
- ✅ **TF-IDF** con similitud coseno
- ✅ **LSA** (Latent Semantic Analysis)
- ✅ **LDA** (Latent Dirichlet Allocation)

**Basados en IA:**
- ✅ **Sentence-BERT** (`all-MiniLM-L6-v2`)
- ✅ **RoBERTa** embeddings

#### Pipeline de Procesamiento:
```
Abstract 1, Abstract 2, Abstract 3
         ↓
 1. Limpieza de texto
    - Lowercase
    - Eliminación de stopwords
    - Lematización
         ↓
 2. Vectorización
    - TF-IDF Matrix
    - Embeddings neuronales
         ↓
 3. Cálculo de Similitud
    - Coseno
    - Distancia euclidiana
         ↓
 4. Ranking de Pares
    - Top 10 más similares
    - Top 10 menos similares
```

#### Outputs:
```
data/processed/
  ├── similitud_resultados.json      # Resultados completos
  ├── reporte_similitud.md           # Reporte Markdown
  └── reporte_similitud_top.csv      # Top pares CSV
```

#### Ejemplo de Output JSON:
```json
{
  "metadata": {
    "execution_date": "2024-11-05 10:30:45",
    "input_indices": [0, 3, 7],
    "algorithms": ["tfidf", "sentence_bert"],
    "total_pairs": 3
  },
  "results": [
    {
      "pair": "0 vs 3",
      "titles": ["Article A", "Article B"],
      "tfidf_similarity": 0.75,
      "sentence_bert_similarity": 0.82,
      "avg_similarity": 0.785
    }
  ]
}
```

---

### 📈 Requerimiento 3: Análisis de Frecuencia

**Objetivo**: Extraer términos relevantes y evaluar su representatividad.

#### Pipeline:
```
BibTeX Corpus
     ↓
1. Términos Semilla (ground truth)
   - "sorting algorithm"
   - "data structure"
   - "computational complexity"
   - ... (15 términos definidos manualmente)
     ↓
2. Cálculo de Frecuencias
   - Por documento: ¿En cuántos aparece?
   - Global: Total de ocurrencias
     ↓
3. Extracción Automática (TF-IDF)
   - max_features=15
   - min_df=2 (mínimo 2 documentos)
   - Vectorización TF-IDF
     ↓
4. Evaluación de Precisión
   - Similitud semántica (embeddings)
   - threshold=0.50
   - Términos auto vs semilla
     ↓
5. Reporte JSON + Consola
```

#### Métricas:
- **Precisión semántica**: % de términos auto-generados relevantes
- **Cobertura**: Términos semilla encontrados en corpus
- **Diversidad**: Varianza en distribución de frecuencias

#### Outputs:
```
requirement_3/
  └── req3_resultados.json
```

#### Ejemplo de Output:
```json
{
  "seed_terms": {
    "sorting algorithm": {
      "frequency": 45,
      "documents": 38
    }
  },
  "auto_terms": {
    "binary search tree": {
      "tfidf_score": 0.87,
      "is_relevant": true
    }
  },
  "evaluation": {
    "precision": 0.73,
    "relevant_count": 11,
    "total_auto": 15
  }
}
```

---

### 🌳 Requerimiento 4: Clustering Jerárquico

**Objetivo**: Agrupar documentos por similitud semántica.

#### Algoritmos:
- ✅ **Agglomerative Clustering** (ward, complete, average linkage)
- ✅ **DBSCAN** (para comparación)

#### Proceso:
```
Corpus (n=25 abstracts)
     ↓
1. Vectorización TF-IDF
     ↓
2. Clustering Jerárquico
   - Linkage: ward, complete, average
     ↓
3. Generación de Dendrogramas
   - Visualización PNG
   - Etiquetas: Autor + Año
     ↓
4. Exportación de Grupos
```

#### Outputs:
```
data/processed/
  ├── dendrogram_ward.png
  ├── dendrogram_complete.png
  ├── dendrogram_average.png
  └── clusters_assignment.json
```

---

### 🗺️ Requerimiento 5: Visualizaciones Avanzadas

**Objetivo**: Generar análisis visual multidimensional.

#### Visualizaciones:

**1. Mapa de Calor Geográfico**
- Distribución de primer autor por país
- Mapa mundial interactivo (Plotly)
- Gráfico de barras top 10 países

**2. Nube de Palabras**
- Abstracts + Keywords
- Máximo 150 palabras
- Stopwords filtradas
- Colores temáticos

**3. Líneas Temporales**
- **Serie 1**: Publicaciones por año
- **Serie 2**: Top 8 revistas por año

**4. Reporte PDF Consolidado**
- Todas las visualizaciones en un PDF
- Metadatos y estadísticas
- Generado con `matplotlib.backends.backend_pdf`

#### Outputs:
```
requirement_5/
  ├── heatmap_geo.png
  ├── heatmap_geo.html        # Interactivo
  ├── wordcloud.png
  ├── timeline_year.png
  ├── timeline_journal.png
  └── reporte_completo.pdf    # Consolidado
```

---

## 🎮 Uso del Sistema

### Opción 1: Ejecutar Todo el Pipeline

```bash
# Ejecutar todos los requerimientos en secuencia
python run_all.py

# Con parámetros personalizados
python run_all.py \
  --bib data/processed/productos_unificados.bib \
  --req2 0 5 10 \
  --req4n 30 \
  --wcmax 200 \
  --topj 10
```

### Opción 2: Ejecutar Requerimientos Individuales

#### Requerimiento 1: Scraping
```bash
python main.py req1
```

#### Seguimiento 1: Algoritmos de Ordenamiento
```bash
python Seguimiento_1/algoritmos_ordenamiento.py
```

#### Requerimiento 2: Similitud
```bash
# Comparar abstracts 0, 3 y 7
python main.py req2 0 3 7

# Comparar más abstracts
python main.py req2 0 5 10 15 20
```

#### Requerimiento 3: Frecuencias
```bash
python main.py req3 --max-terms 20 --min-df 3 --thr 0.60
```

#### Requerimiento 4: Clustering
```bash
python main.py req4 --n 25
```

#### Requerimiento 5: Visualizaciones
```bash
python main.py req5 --wc-max 150 --topj 8
```

### Opción 3: Ver Ayuda

```bash
# Ayuda general
python main.py --help

# Ayuda por comando
python main.py req2 --help
python main.py req3 --help
```

---

## 🌐 Interfaz Web

El proyecto incluye una **interfaz web Flask** para ejecutar análisis sin CLI.

### Iniciar el Servidor

```bash
python webui.py
```

Abre tu navegador en: **http://127.0.0.1:5000**

### Funcionalidades Web:

- ✅ **Dashboard Interactivo**: Vista general de todos los requerimientos
- ✅ **Ejecución de Scripts**: Botones para cada requerimiento
- ✅ **Visualización de Resultados**: Imágenes y gráficos embebidos
- ✅ **Descarga de Archivos**: CSV, JSON, PDF, PNG
- ✅ **Logs en Tiempo Real**: Ver progreso de ejecución
- ✅ **Responsive Design**: Compatible con móviles

### Capturas de Pantalla:

```
┌─────────────────────────────────────────┐
│  📊 Sistema de Análisis Bibliométrico   │
├─────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  Req1  │ │  Req2  │ │  Req3  │       │
│  │ [Run]  │ │ [Run]  │ │ [Run]  │       │
│  └────────┘ └────────┘ └────────┘       │
│                                         │
│  📈 Resultados Recientes:               │
│  • productos_unificados.bib (2.1 MB)    │
│  • similitud_resultados.json (145 KB)   │
│  • dendrogram_ward.png (256 KB)         │
│                                         │
│  📥 Descargar Todos los Resultados      │
└─────────────────────────────────────────┘
```

---

## 📊 Metodología Científica

### Diseño Experimental

**Pregunta de Investigación:**
> ¿Cómo se comparan los algoritmos de ordenamiento clásicos en datasets bibliográficos reales?

**Hipótesis:**
- H1: TimSort será el más eficiente (O(n log n) híbrido)
- H2: Algoritmos cuadráticos (Selection, Gnome) serán los más lentos
- H3: Radix Sort tendrá buen desempeño teórico pero overhead práctico

**Variables:**
- **Independiente**: Algoritmo de ordenamiento
- **Dependiente**: Tiempo de ejecución (segundos)
- **Controladas**: Dataset (mismo BibTeX), hardware, Python 3.11

### Resultados Estadísticos

#### Análisis de Tiempos:

| Categoría | Algoritmo | Tiempo (s) | Speedup vs Peor |
|-----------|-----------|------------|-----------------|
| **Óptimos** | TimSort | 0.0078 | 1059x |
| | QuickSort | 0.0150 | 550x |
| | Gnome Sort | 0.0329 | 251x |
| **Buenos** | Tree Sort | 0.0820 | 101x |
| | Comb Sort | 0.0899 | 92x |
| | Binary Insertion | 0.0929 | 89x |
| **Aceptables** | Pigeonhole | 0.1827 | 45x |
| | Bucket Sort | 0.2252 | 37x |
| | Bitonic Sort | 0.3603 | 23x |
| **Lentos** | Heap Sort | 1.4785 | 5.6x |
| | Radix Sort | 2.3607 | 3.5x |
| **Muy Lentos** | Selection Sort | 8.2562 | 1x |

#### Conclusiones:

1. **TimSort es el claro ganador** (implementación nativa de Python)
2. **QuickSort** tiene excelente balance complejidad/velocidad
3. **Selection Sort** es el peor por su O(n²) puro
4. **Radix Sort** tiene overhead de memoria y buckets
5. **Heap Sort** sufre por constantes multiplicativas grandes

---

## 📦 Resultados y Outputs

### Directorio de Salidas

```
data/processed/
├── productos_unificados.bib         # Dataset unificado (1500+ entradas)
├── ordenamiento/                    # 12 archivos ordenados
│   ├── ordenado_timsort.bib
│   └── ...
├── similitud_resultados.json        # Matrices de similitud
├── req3_resultados.json             # Frecuencias y términos
├── clusters_assignment.json         # Grupos jerárquicos
└── reporte_completo.pdf             # Reporte consolidado
```

### Métricas de Desempeño

#### Scraping (Req1):
- **Tiempo promedio**: 5-10 min por búsqueda
- **Artículos extraídos**: 1500+ (ACM + SAGE)
- **Tasa de éxito**: >95%

#### Ordenamiento (Seg1):
- **Dataset**: 1522 entradas BibTeX
- **Algoritmo más rápido**: TimSort (7.8 ms)
- **Algoritmo más lento**: Selection Sort (8.26 s)

#### Similitud (Req2):
- **Modelos evaluados**: 5 (TF-IDF, LSA, LDA, SBERT, RoBERTa)
- **Tiempo por par**: ~0.5s (SBERT)
- **Precisión promedio**: 85% (validación manual)

#### Frecuencias (Req3):
- **Términos semilla**: 15
- **Términos extraídos**: 15 (TF-IDF)
- **Precisión semántica**: 73%

#### Clustering (Req4):
- **Abstracts analizados**: 25
- **Linkages evaluados**: 3 (ward, complete, average)
- **Tiempo de clustering**: <2s

#### Visualizaciones (Req5):
- **Países mapeados**: 45+
- **Palabras en nube**: 150
- **Líneas temporales**: 2 (año, revista)
- **Tamaño PDF**: ~2 MB

---

## 🐛 Troubleshooting

### Problema 1: ChromeDriver no funciona

**Síntoma:**
```
selenium.common.exceptions.SessionNotCreatedException: 
Message: session not created: This version of ChromeDriver only supports Chrome version 120
```

**Solución:**
```bash
# Actualizar Chrome a la última versión
# Reinstalar undetected-chromedriver
pip install --upgrade undetected-chromedriver
```

---

### Problema 2: Error de memoria (MemoryError)

**Síntoma:**
```
MemoryError: Unable to allocate array with shape (10000, 10000)
```

**Solución:**
```python
# En requirement_2/classic.py, reducir n_samples
# Cambiar de 1000 a 500
n_samples = min(500, len(corpus))
```

---

### Problema 3: Modelos de IA no descargan

**Síntoma:**
```
OSError: Can't load tokenizer for 'sentence-transformers/all-MiniLM-L6-v2'
```

**Solución:**
```bash
# Verificar conexión a internet
ping huggingface.co

# Descargar manualmente
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

### Problema 4: Gráficos no se generan

**Síntoma:**
```
RuntimeError: Invalid DISPLAY variable
```

**Solución:**
```bash
# En entornos sin GUI (servidores)
export MPLBACKEND=Agg

# O en Python
import matplotlib
matplotlib.use('Agg')
```

---

### Problema 5: Error de encoding en Windows

**Síntoma:**
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81
```

**Solución:**
```bash
# Configurar UTF-8 globalmente (Windows 10+)
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

# O ejecutar con:
python -X utf8 main.py req1
```

---

## 🤝 Contribuciones

### Autores

- **Néstor Castelblancon** - [@nestorcastelblanco](https://github.com/nestorcastelblanco)
- **Sebastián Agudelo** - [@sebastianagudelom](https://github.com/sebastianagudelom)
- **Juan Felipe Hurtado** - [@felipehurtadoo](https://github.com/felipehurtadoo)

### Cómo Contribuir

1. **Fork** el proyecto
2. Crear una **rama** para tu feature (`git checkout -b feature/amazing-feature`)
3. **Commit** tus cambios (`git commit -m 'Add amazing feature'`)
4. **Push** a la rama (`git push origin feature/amazing-feature`)
5. Abrir un **Pull Request**

### Código de Conducta

Este es un proyecto académico. Por favor:
- ✅ Documenta tu código
- ✅ Escribe tests
- ✅ Mantén PEP 8
- ✅ Respeta las licencias de librerías

---

## 📜 Licencia

Este proyecto es de uso **académico exclusivo**.

**Restricciones:**
- ❌ No usar para fines comerciales
- ❌ No redistribuir sin permiso
- ✅ Citar al usar en trabajos académicos

**Cita sugerida:**
```bibtex
@software{bibliometria_aa_2024,
  author = {Castelblanco, Néstor; Agudelo, Sebastián and Hurtado, Felipe},
  title = {Sistema de Análisis Bibliométrico y Algoritmos de Ordenamiento},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/nestorcastelblanco/Bibliometria_AA}
}
```

---

## 📞 Contacto

**Repositorio**: [github.com/nestorcastelblanco/Bibliometria_AA](https://github.com/nestorcastelblanco/Bibliometria_AA)

**Issues**: [Reportar un problema](https://github.com/nestorcastelblanco/Bibliometria_AA/issues)

---

## 🙏 Agradecimientos

- **Python Software Foundation** - Por Python
- **Selenium Project** - Por automatización web
- **HuggingFace** - Por modelos pre-entrenados
- **Plotly** - Por visualizaciones interactivas
- **ACM & SAGE** - Por acceso a bases de datos académicas

---

## 📚 Referencias Bibliográficas

1. Knuth, D. E. (1998). *The Art of Computer Programming, Volume 3: Sorting and Searching*. Addison-Wesley.
2. Cormen, T. H., et al. (2009). *Introduction to Algorithms*. MIT Press.
3. Manning, C. D., et al. (2008). *Introduction to Information Retrieval*. Cambridge University Press.
4. Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP.

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

Made with ❤️ for we

</div>
