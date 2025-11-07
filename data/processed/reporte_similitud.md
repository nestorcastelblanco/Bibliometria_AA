# Reporte de Similitud Textual

**Algoritmo principal:** GTE (coseno)
**Pares totales:** 3

## Selección de artículos
- [1] Machine Learning on Graphs in the Era of Generative Artificial Intelligence
- [2] Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving
- [3] Experiencing Art Museum with a Generative Artificial Intelligence Chatbot

## Estadísticas generales

| Métrica | Valor |
|---|---:|
| n | 3 |
| min | 80.4% |
| max | 83.6% |
| media | 82.1% |
| mediana | 82.4% |

### Distribución por rangos

| Rango | Conteo |
|---|---:|
| ≥0.80 | 3 |
| 0.60–0.79 | 0 |
| 0.40–0.59 | 0 |
| 0.20–0.39 | 0 |
| <0.20 | 0 |

## Top 3 pares por GTE (coseno) (Algoritmo Principal)

| Rank | Índices (i,j) | % Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | 2,3 | 83.6% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 2 | 1,3 | 82.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 3 | 1,2 | 80.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |

## Comparación de los 6 Algoritmos

### Todos los pares comparados

**Algoritmos Clásicos (4):**
- **Levenshtein**: Distancia de edición (inserción, eliminación, sustitución)
- **Damerau-Levenshtein**: Levenshtein + transposición de caracteres adyacentes
- **Jaccard**: Similitud de conjuntos de tokens (intersección / unión)
- **Coseno TF-IDF**: Vectorización estadística con pesos TF-IDF

**Algoritmos con IA (2):**
- **SBERT**: Sentence-BERT embeddings (all-MiniLM-L6-v2)
- **GTE**: General Text Embeddings (thenlper/gte-small)

| Par (i,j) | Levenshtein (normalizada) | Damerau–Levenshtein (normalizada) | Jaccard (tokens) | Coseno (TF-IDF) | SBERT (coseno) | GTE (coseno) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| (2,3) | 25.2% | 25.2% | 9.4% | 4.3% | 38.6% | 83.6% |
| (1,3) | 27.4% | 27.4% | 5.4% | 3.2% | 30.1% | 82.4% |
| (1,2) | 27.2% | 27.4% | 5.8% | 4.7% | 25.9% | 80.4% |

### Estadísticas por Algoritmo

| Algoritmo | Media | Mediana | Min | Max |
|---|:--:|:--:|:--:|:--:|
| Levenshtein (normalizada) | 26.6% | 27.2% | 25.2% | 27.4% |
| Damerau–Levenshtein (normalizada) | 26.7% | 27.4% | 25.2% | 27.4% |
| Jaccard (tokens) | 6.9% | 5.8% | 5.4% | 9.4% |
| Coseno (TF-IDF) | 4.1% | 4.3% | 3.2% | 4.7% |
| SBERT (coseno) | 31.5% | 30.1% | 25.9% | 38.6% |
| GTE (coseno) | 82.1% | 82.4% | 80.4% | 83.6% |

### Análisis de Divergencias entre Algoritmos

Los algoritmos **clásicos** (basados en caracteres y tokens) suelen dar scores **bajos** porque:
- Solo detectan coincidencias exactas de palabras
- No capturan similitud semántica (sinónimos, paráfrasis)
- Son sensibles a diferencias de redacción

Los algoritmos **con IA** (SBERT, GTE) dan scores **más altos** porque:
- Capturan significado semántico de los textos
- Detectan similitud conceptual aunque las palabras sean diferentes
- Están entrenados en millones de textos para aprender relaciones semánticas

## Ranking por Algoritmo Individual

A continuación se muestra el ranking de los pares según cada uno de los 6 algoritmos:

### Levenshtein (normalizada)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (1,3) | 27.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 2 | (1,2) | 27.2% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |
| 3 | (2,3) | 25.2% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |

### Damerau–Levenshtein (normalizada)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (1,2) | 27.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |
| 2 | (1,3) | 27.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 3 | (2,3) | 25.2% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |

### Jaccard (tokens)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (2,3) | 9.4% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 2 | (1,2) | 5.8% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |
| 3 | (1,3) | 5.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |

### Coseno (TF-IDF)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (1,2) | 4.7% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |
| 2 | (2,3) | 4.3% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 3 | (1,3) | 3.2% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |

### SBERT (coseno)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (2,3) | 38.6% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 2 | (1,3) | 30.1% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 3 | (1,2) | 25.9% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |

### GTE (coseno)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (2,3) | 83.6% | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 2 | (1,3) | 82.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Experiencing Art Museum with a Generative Artificial Intelligence Chatbot |
| 3 | (1,2) | 80.4% | Machine Learning on Graphs in the Era of Generative Artificial Intelligence | Analyzing Students' Use of Generative Artificial Intelligence in Collaborative Problem Solving |

## Apéndice — ¿Cómo se calculan las similitudes?

### Levenshtein (normalizada)

- Mide la distancia de edición mínima entre dos textos (insertar, borrar, sustituir).
- Se usa programación dinámica con una matriz dp de tamaño (m+1)x(n+1).
- La similitud se normaliza: sim = 1 - dist/max(|a|,|b|).

### Damerau–Levenshtein (normalizada)

- Extiende Levenshtein añadiendo la operación de transposición (intercambio de adyacentes).
- Usa DP y compara también dp[i-2][j-2] + 1 cuando hay transposición.
- Se normaliza igual: sim = 1 - dist/max(|a|,|b|).

### Jaccard (tokens)

- Convierte cada texto a un conjunto de palabras (tokens) sin repeticiones.
- Calcula |A∩B|/|A∪B| en [0,1].
- Mide traslape del vocabulario, sin considerar orden ni frecuencia.

### Coseno (TF-IDF)

- Construye vectores TF-IDF por documento: v_d[t] = tf_d(t)*idf(t).
- idf(t) ≈ log((N+1)/(df(t)+1)) + 1; TF es frecuencia relativa.
- La similitud es el coseno entre vectores (x·y)/(||x||·||y||).

### SBERT (coseno)

- Cada texto se transforma en un embedding (vector) con Sentence-BERT.
- Se normaliza el vector y se aplica coseno entre embeddings.
- Captura similitud semántica (sinónimos/paráfrasis).

### GTE (coseno)

- Modelo de embeddings reciente (thenlper/gte-small).
- Convierte cada texto en un embedding; similitud por coseno.
- Gratis y rápido; buen desempeño semántico.
