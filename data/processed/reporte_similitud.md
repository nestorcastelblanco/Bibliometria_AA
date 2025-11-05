# Reporte de Similitud Textual

**Algoritmo principal:** GTE (coseno)
**Pares totales:** 3

## Selección de artículos
- [0] Generative Artificial Intelligence Policies under the Microscope
- [3] The relationship between generative artificial intelligence and cybersecurity
- [7] Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence

## Estadísticas generales

| Métrica | Valor |
|---|---:|
| n | 3 |
| min | 76.0% |
| max | 83.3% |
| media | 79.4% |
| mediana | 78.9% |

### Distribución por rangos

| Rango | Conteo |
|---|---:|
| ≥0.80 | 1 |
| 0.60–0.79 | 2 |
| 0.40–0.59 | 0 |
| 0.20–0.39 | 0 |
| <0.20 | 0 |

## Top 3 pares por GTE (coseno) (Algoritmo Principal)

| Rank | Índices (i,j) | % Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | 3,7 | 83.3% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | 0,7 | 78.9% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 3 | 0,3 | 76.0% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |

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
| (3,7) | 31.9% | 31.9% | 9.2% | 24.2% | 35.7% | 83.3% |
| (0,7) | 7.9% | 7.9% | 1.4% | 1.2% | 12.3% | 78.9% |
| (0,3) | 8.5% | 8.5% | 0.0% | 0.0% | 14.8% | 76.0% |

### Estadísticas por Algoritmo

| Algoritmo | Media | Mediana | Min | Max |
|---|:--:|:--:|:--:|:--:|
| Levenshtein (normalizada) | 16.1% | 8.5% | 7.9% | 31.9% |
| Damerau–Levenshtein (normalizada) | 16.1% | 8.5% | 7.9% | 31.9% |
| Jaccard (tokens) | 3.5% | 1.4% | 0.0% | 9.2% |
| Coseno (TF-IDF) | 8.5% | 1.2% | 0.0% | 24.2% |
| SBERT (coseno) | 20.9% | 14.8% | 12.3% | 35.7% |
| GTE (coseno) | 79.4% | 78.9% | 76.0% | 83.3% |

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
| 1 | (3,7) | 31.9% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,3) | 8.5% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |
| 3 | (0,7) | 7.9% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |

### Damerau–Levenshtein (normalizada)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (3,7) | 31.9% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,3) | 8.5% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |
| 3 | (0,7) | 7.9% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |

### Jaccard (tokens)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (3,7) | 9.2% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,7) | 1.4% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 3 | (0,3) | 0.0% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |

### Coseno (TF-IDF)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (3,7) | 24.2% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,7) | 1.2% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 3 | (0,3) | 0.0% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |

### SBERT (coseno)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (3,7) | 35.7% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,3) | 14.8% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |
| 3 | (0,7) | 12.3% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |

### GTE (coseno)

| Rank | Par (i,j) | Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | (3,7) | 83.3% | The relationship between generative artificial intelligence and cybersecurity | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 2 | (0,7) | 78.9% | Generative Artificial Intelligence Policies under the Microscope | Behavioral Analysis of Classroom Interactions Supported by Generative Artificial Intelligence |
| 3 | (0,3) | 76.0% | Generative Artificial Intelligence Policies under the Microscope | The relationship between generative artificial intelligence and cybersecurity |

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
