"""
Módulo de algoritmos clásicos de similitud textual.

Implementa algoritmos tradicionales de similitud:
- Levenshtein: Distancia de edición (inserción, eliminación, sustitución)
- Damerau-Levenshtein: Levenshtein + transposición de caracteres adyacentes
- Jaccard: Similitud basada en conjuntos de tokens
- Coseno TF-IDF: Similitud vectorial con pesos TF-IDF

Todos normalizados a rango [0, 1] para comparación consistente.

Parte del Requerimiento 2: Comparación de algoritmos de similitud textual.
"""
from __future__ import annotations
from typing import Dict, Any
from .similarity_base import SimilarityAlgorithm
from .preprocessing import Preprocessor
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

_pp = Preprocessor()

class LevenshteinSim(SimilarityAlgorithm):
    """
    Algoritmo de similitud basado en distancia de edición de Levenshtein.
    
    Calcula distancia mínima de edición (número de operaciones para transformar
    un texto en otro) y normaliza a [0,1] para obtener score de similitud.
    
    Operaciones permitidas:
        - Inserción de un carácter
        - Eliminación de un carácter
        - Sustitución de un carácter
    
    Attributes:
        name (str): Nombre identificador del algoritmo
    
    Fórmula:
        similitud = 1 - (distancia / max(len(a), len(b)))
    
    Complejidad:
        - Tiempo: O(m * n) donde m, n son longitudes de textos
        - Espacio: O(m * n) para matriz de programación dinámica
    
    Ventajas:
        - Preciso para detectar errores tipográficos
        - No requiere tokenización
        - Funciona bien con textos cortos
    
    Desventajas:
        - No captura similitud semántica
        - Sensible a orden de caracteres
        - Computacionalmente costoso para textos largos
    """
    name = "Levenshtein (normalizada)"

    def _dist(self, a: str, b: str) -> int:
        """
        Calcula distancia de Levenshtein usando programación dinámica.
        
        Implementa algoritmo de Wagner-Fischer para calcular número mínimo
        de operaciones de edición (inserción, eliminación, sustitución).
        
        Args:
            a (str): Primer string
            b (str): Segundo string
        
        Returns:
            int: Distancia de edición mínima (número de operaciones)
        
        Algorithm:
            1. Crea matriz dp de (m+1) x (n+1)
            2. Inicializa primera fila y columna (casos base)
            3. Para cada celda dp[i][j]:
               - Si caracteres coinciden: dp[i-1][j-1]
               - Si no: min de insertar, eliminar, sustituir + 1
            4. Retorna dp[m][n] (esquina inferior derecha)
        
        Example:
            >>> lev = LevenshteinSim()
            >>> lev._dist("kitten", "sitting")
            3  # k→s, e→i, +g
            >>> lev._dist("hello", "hello")
            0
        
        Notas:
            - Método privado, usado internamente por score()
            - Matriz dp[i][j] = distancia entre a[:i] y b[:j]
            - Casos base: dp[i][0] = i, dp[0][j] = j
            - Cost = 0 si caracteres iguales, 1 si diferentes
        """
        a, b = a or "", b or ""
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(m+1): dp[i][0] = i
        for j in range(n+1): dp[0][j] = j
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost = 0 if a[i-1] == b[j-1] else 1
                dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
        return dp[m][n]

    def score(self, a: str, b: str) -> float:
        """
        Calcula score de similitud normalizado basado en distancia de Levenshtein.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Similitud en [0, 1]
                  1.0 = textos idénticos
                  0.0 = completamente diferentes
        
        Process:
            1. Limpia ambos textos con preprocesador
            2. Si ambos vacíos: retorna 1.0 (idénticos)
            3. Calcula distancia de Levenshtein
            4. Normaliza: sim = 1 - (dist / max_length)
        
        Example:
            >>> lev = LevenshteinSim()
            >>> lev.score("machine learning", "machine learning")
            1.0
            >>> lev.score("kitten", "sitting")
            0.571  # 3 edits / 7 chars
        
        Notas:
            - Aplica preprocesamiento (minúsculas, sin puntuación)
            - Normalización hace scores comparables entre pares
            - max_length evita división por cero
        """
        a, b = _pp.clean(a), _pp.clean(b)
        if not a and not b: return 1.0
        d = self._dist(a, b)
        L = max(len(a), len(b))
        return 1 - d/L

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación detallada del cálculo de similitud.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Dict[str, Any]: Detalles del cálculo
                - formula: Fórmula usada
                - dist: Distancia de edición calculada
                - maxlen: Longitud máxima de los textos
                - normalized: Score final normalizado
        
        Example:
            >>> lev = LevenshteinSim()
            >>> lev.explain("cat", "bat")
            {'formula': '1 - dist/maxlen', 'dist': 1, 
             'maxlen': 3, 'normalized': 0.6667}
        """
        a2, b2 = _pp.clean(a), _pp.clean(b)
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return {"formula": "1 - dist/maxlen", "dist": d, "maxlen": L, "normalized": 1 - (d/L) if L else 1.0}

class DamerauLevenshteinSim(SimilarityAlgorithm):
    """
    Algoritmo de similitud basado en distancia de Damerau-Levenshtein.
    
    Extensión de Levenshtein que añade transposición (intercambio de caracteres
    adyacentes) como operación de edición, más realista para errores tipográficos.
    
    Operaciones permitidas:
        - Inserción de un carácter
        - Eliminación de un carácter
        - Sustitución de un carácter
        - Transposición de dos caracteres adyacentes
    
    Attributes:
        name (str): Nombre identificador del algoritmo
    
    Fórmula:
        similitud = 1 - (distancia_DL / max(len(a), len(b)))
    
    Ventajas sobre Levenshtein:
        - Más preciso para errores de digitación reales
        - Transposición frecuente en typos (ej: "teh" → "the")
        - Cuenta 1 operación vs 2 en Levenshtein clásico
    
    Example de transposición:
        "ab" → "ba": 
        - Levenshtein: 2 operaciones (sustituir ambos)
        - Damerau-Levenshtein: 1 operación (transponer)
    """
    name = "Damerau–Levenshtein (normalizada)"

    def _dist(self, a: str, b: str) -> int:
        """
        Calcula distancia de Damerau-Levenshtein con programación dinámica.
        
        Similar a Levenshtein pero considera transposiciones de caracteres
        adyacentes como una sola operación.
        
        Args:
            a (str): Primer string
            b (str): Segundo string
        
        Returns:
            int: Distancia de edición mínima con transposiciones
        
        Algorithm:
            1. Inicializa matriz dp igual que Levenshtein
            2. Para cada celda, calcula min de:
               - Inserción: dp[i-1][j] + 1
               - Eliminación: dp[i][j-1] + 1
               - Sustitución: dp[i-1][j-1] + cost
               - Transposición: dp[i-2][j-2] + 1 (si aplica)
            3. Transposición válida si a[i-1]==b[j-2] y a[i-2]==b[j-1]
        
        Example:
            >>> dl = DamerauLevenshteinSim()
            >>> dl._dist("ab", "ba")
            1  # transposición
            >>> dl._dist("abc", "bac")
            1  # transposición de 'a' y 'b'
        
        Notas:
            - Método privado, usado internamente por score()
            - Transposición solo entre caracteres adyacentes
            - Más costoso que Levenshtein pero más preciso
        """
        a, b = a or "", b or ""
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(m+1): dp[i][0] = i
        for j in range(n+1): dp[0][j] = j
        for i in range(1, m+1):
            for j in range(1, n+1):
                cost = 0 if a[i-1] == b[j-1] else 1
                dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
                if i>1 and j>1 and a[i-1]==b[j-2] and a[i-2]==b[j-1]:
                    dp[i][j] = min(dp[i][j], dp[i-2][j-2] + 1)  # transposición
        return dp[m][n]

    def score(self, a: str, b: str) -> float:
        """
        Calcula score de similitud normalizado con Damerau-Levenshtein.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Similitud en [0, 1] considerando transposiciones
        
        Process:
            1. Limpia ambos textos con preprocesador
            2. Si ambos vacíos: retorna 1.0
            3. Calcula distancia de Damerau-Levenshtein
            4. Normaliza: sim = 1 - (dist / max_length)
        
        Example:
            >>> dl = DamerauLevenshteinSim()
            >>> dl.score("the", "teh")
            0.667  # 1 transposición / 3 chars
            >>> dl.score("abc", "bac")
            0.667  # 1 transposición / 3 chars
        """
        a2, b2 = _pp.clean(a), _pp.clean(b)
        if not a2 and not b2: return 1.0
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return 1 - d/L

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación detallada del cálculo con transposiciones.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Dict[str, Any]: Detalles del cálculo incluyendo transposiciones
                - formula: Fórmula usada
                - includes: Operaciones consideradas
                - dist: Distancia calculada
                - normalized: Score final
        """
        a2, b2 = _pp.clean(a), _pp.clean(b)
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return {"formula": "1 - DL/maxlen", "includes": "transposición", "dist": d,
                "normalized": 1 - (d/L) if L else 1.0}

class JaccardTokens(SimilarityAlgorithm):
    """
    Algoritmo de similitud basado en índice de Jaccard de conjuntos de tokens.
    
    Mide similitud como proporción de tokens compartidos sobre tokens únicos
    totales. Ignora frecuencia y orden, solo considera presencia/ausencia.
    
    Attributes:
        name (str): Nombre identificador del algoritmo
    
    Fórmula:
        Jaccard(A, B) = |A ∩ B| / |A ∪ B|
        Donde A, B son conjuntos de tokens únicos
    
    Características:
        - Rango: [0, 1] naturalmente
        - Simétrico: J(A,B) = J(B,A)
        - Ignora frecuencias (solo presencia)
        - Ignora orden de palabras
    
    Ventajas:
        - Simple y eficiente
        - Bueno para medir traslape de vocabulario
        - No requiere corpus para training
    
    Desventajas:
        - No captura similitud semántica
        - Ignora contexto y orden
        - Penaliza diferencias en longitud
    """
    name = "Jaccard (tokens)"

    def score(self, a: str, b: str) -> float:
        """
        Calcula similitud de Jaccard entre conjuntos de tokens.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Índice de Jaccard en [0, 1]
                  1.0 = vocabularios idénticos
                  0.0 = sin tokens en común
        
        Process:
            1. Tokeniza ambos textos (limpieza + split + filtro stopwords)
            2. Convierte a conjuntos (elimina duplicados)
            3. Calcula intersección: tokens en ambos
            4. Calcula unión: todos los tokens únicos
            5. Retorna |intersección| / |unión|
        
        Example:
            >>> jac = JaccardTokens()
            >>> jac.score("machine learning", "machine learning")
            1.0
            >>> jac.score("machine learning", "deep learning")
            0.5  # 'learning' común, 3 únicos total
            >>> jac.score("cat", "dog")
            0.0
        
        Notas:
            - Usa preprocesador para tokenización consistente
            - Stopwords filtradas automáticamente
            - Ambos vacíos = 1.0 (convención)
            - División por cero evitada (union=0 → score=0)
        """
        A = set(_pp.tokenize(a)); B = set(_pp.tokenize(b))
        if not A and not B: return 1.0
        inter = len(A & B); union = len(A | B)
        return inter/union if union else 0.0

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación detallada del cálculo de Jaccard.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Dict[str, Any]: Detalles del cálculo
                - formula: Fórmula de Jaccard
                - |A|: Tamaño del conjunto A
                - |B|: Tamaño del conjunto B
                - inter: Tamaño de intersección
                - union: Tamaño de unión
                - shared_tokens: Lista de tokens compartidos (máx 25)
        
        Example:
            >>> jac = JaccardTokens()
            >>> jac.explain("machine learning", "deep learning")
            {'formula': '|A∩B|/|A∪B|', '|A|': 2, '|B|': 2,
             'inter': 1, 'union': 3, 'shared_tokens': ['learning']}
        """
        A = set(_pp.tokenize(a)); B = set(_pp.tokenize(b))
        return {"formula": "|A∩B|/|A∪B|", "|A|": len(A), "|B|": len(B),
                "inter": len(A & B), "union": len(A | B),
                "shared_tokens": sorted(list(A & B))[:25]}

# requirement_2/classic.py
class CosineTFIDF(SimilarityAlgorithm):
    """
    Algoritmo de similitud coseno con vectorización TF-IDF.
    
    Representa textos como vectores TF-IDF y calcula similitud coseno.
    TF-IDF pondera términos por frecuencia e inversa de frecuencia documental.
    
    Attributes:
        name (str): Nombre identificador del algoritmo
        vec (TfidfVectorizer): Vectorizador TF-IDF de sklearn
    
    TF-IDF (Term Frequency - Inverse Document Frequency):
        - TF: Frecuencia de término en documento
        - IDF: log((N+1)/(df+1)) + 1, donde N=docs, df=docs con término
        - TF-IDF = TF * IDF
    
    Similitud Coseno:
        cos(θ) = (A · B) / (||A|| * ||B||)
        Rango: [0, 1] con normalización L2
    
    Ventajas:
        - Pondera términos raros más que comunes
        - Estándar de la industria para recuperación de información
        - Ignora longitud de documentos (normalización)
    
    Desventajas:
        - No captura similitud semántica profunda
        - Requiere al menos 2 documentos para fit
        - Sensible a vocabulario fuera de corpus
    """
    name = "Coseno (TF-IDF)"

    def __init__(self):
        """
        Inicializa vectorizador TF-IDF con tokenizador personalizado.
        
        Configura TfidfVectorizer para usar preprocesador del módulo,
        evitando preprocesamiento duplicado y warnings de sklearn.
        
        Configuración:
            - tokenizer: usa _pp.tokenize (limpieza + stopwords)
            - preprocessor: None (limpieza ya hecha en tokenizer)
            - lowercase: False (ya aplicado en Preprocessor)
            - stop_words: None (ya filtrados en tokenizer)
            - token_pattern: None (evita regex default de sklearn)
        
        Notas:
            - TfidfVectorizer se fit por cada llamada a score()
            - Vectorizador debe refittearse para cada par (no corpus fijo)
            - Configuración evita warnings de sklearn sobre custom tokenizer
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vec = TfidfVectorizer(
            tokenizer=_pp.tokenize,  # usamos tu tokenizador
            preprocessor=None,       # ya limpias en tokenize
            lowercase=False,         # ya haces lowercase en Preprocessor
            stop_words=None,         # ya filtras stopwords en tokenize
            token_pattern=None       # <- para que no haya warning
        )

    def score(self, a: str, b: str) -> float:
        """
        Calcula similitud coseno entre vectores TF-IDF de dos textos.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Similitud coseno en [0, 1]
                  1.0 = vectores idénticos (mismo contenido ponderado)
                  0.0 = vectores ortogonales (sin términos comunes)
        
        Process:
            1. Fit vectorizador TF-IDF con ambos textos
            2. Transforma textos a vectores TF-IDF sparse
            3. Calcula similitud coseno entre vectores
            4. Retorna score normalizado
        
        Example:
            >>> cos_tfidf = CosineTFIDF()
            >>> cos_tfidf.score("machine learning models", "machine learning")
            0.82  # alta similitud, términos compartidos
            >>> cos_tfidf.score("cat dog", "programming language")
            0.0  # sin términos comunes
        
        Notas:
            - Vectorizador se refitta para cada par (corpus = 2 docs)
            - IDF con solo 2 docs es limitado pero funcional
            - Términos raros (únicos a un doc) reciben mayor peso
            - Normalización L2 automática en TfidfVectorizer
        """
        from sklearn.metrics.pairwise import cosine_similarity
        X = self.vec.fit_transform([a, b])
        return float(cosine_similarity(X[0], X[1])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación con top términos TF-IDF de cada texto.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Dict[str, Any]: Detalles del cálculo
                - formula: Descripción del método
                - top_tfidf_a: Top 10 términos con mayor peso en texto A
                - top_tfidf_b: Top 10 términos con mayor peso en texto B
        
        Cada término incluye: (palabra, peso_tfidf)
        
        Example:
            >>> cos_tfidf = CosineTFIDF()
            >>> info = cos_tfidf.explain("machine learning", "deep learning")
            >>> info['top_tfidf_a']
            [('machine', 0.707), ('learning', 0.707)]
            >>> info['top_tfidf_b']
            [('deep', 0.707), ('learning', 0.707)]
        
        Notas:
            - Útil para entender qué términos dominan la similitud
            - Pesos altos = términos distintivos del documento
            - Lista limitada a top 10 para legibilidad
            - Ordenados por peso descendente
        """
        X = self.vec.fit_transform([a, b])
        vocab = {v: k for k, v in self.vec.vocabulary_.items()}
        v0 = X[0].tocoo(); v1 = X[1].tocoo()
        tfidf0 = sorted([(vocab[i], float(w)) for i, w in zip(v0.col, v0.data)], key=lambda x: -x[1])[:10]
        tfidf1 = sorted([(vocab[i], float(w)) for i, w in zip(v1.col, v1.data)], key=lambda x: -x[1])[:10]
        return {"formula": "cos(x,y) sobre TF-IDF", "top_tfidf_a": tfidf0, "top_tfidf_b": tfidf1}
