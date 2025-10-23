# Reporte de Similitud Textual

**Algoritmo principal:** GTE (coseno)
**Pares totales:** 3

## Selección de artículos
- [0] {G}enerative {A}rtificial {I}ntelligence {P}olicies under the {M}icroscope
- [3] {T}he relationship between generative artificial intelligence and cybersecurity
- [7] {B}ehavioral {A}nalysis of {C}lassroom {I}nteractions {S}upported by {G}enerative {A}rtificial {I}ntelligence

## Estadísticas generales

| Métrica | Valor |
|---|---:|
| n | 3 |
| min | 76.2% |
| max | 83.6% |
| media | 79.6% |
| mediana | 79.0% |

### Distribución por rangos

| Rango | Conteo |
|---|---:|
| ≥0.80 | 1 |
| 0.60–0.79 | 2 |
| 0.40–0.59 | 0 |
| 0.20–0.39 | 0 |
| <0.20 | 0 |

## Top 3 pares por GTE (coseno)

| Rank | Índices (i,j) | % Similitud | Título i | Título j |
|---:|:---:|---:|---|---|
| 1 | 3,7 | 83.6% | {T}he relationship between generative artificial intelligence and cybersecurity | {B}ehavioral {A}nalysis of {C}lassroom {I}nteractions {S}upported by {G}enerative {A}rtificial {I}ntelligence |
| 2 | 0,7 | 79.0% | {G}enerative {A}rtificial {I}ntelligence {P}olicies under the {M}icroscope | {B}ehavioral {A}nalysis of {C}lassroom {I}nteractions {S}upported by {G}enerative {A}rtificial {I}ntelligence |
| 3 | 0,3 | 76.2% | {G}enerative {A}rtificial {I}ntelligence {P}olicies under the {M}icroscope | {T}he relationship between generative artificial intelligence and cybersecurity |

## Comparación de algoritmos (para los Top anteriores)

| i,j | Levenshtein (normalizada) | Damerau–Levenshtein (normalizada) | Jaccard (tokens) | Coseno (TF-IDF) | SBERT (coseno) | GTE (coseno) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 3,7 | 32.2% | 32.2% | 10.0% | 24.4% | 36.8% | 83.6% |
| 0,7 | 7.8% | 7.8% | 1.4% | 1.2% | 14.6% | 79.0% |
| 0,3 | 8.4% | 8.4% | 0.0% | 0.0% | 15.6% | 76.2% |

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
