"""
Módulo de algoritmos de similitud basados en embeddings de IA.

Implementa algoritmos de similitud textual usando modelos de embeddings
de última generación (Sentence-BERT y GTE) con similitud coseno.

Modelos disponibles:
- SBERT: Sentence-BERT (all-MiniLM-L6-v2)
- GTE: General Text Embeddings (thenlper/gte-small)

Parte del Requerimiento 2: Comparación de algoritmos de similitud textual.
"""
from __future__ import annotations
from typing import Dict, Any
from .similarity_base import SimilarityAlgorithm

class SBERTSim(SimilarityAlgorithm):
    """
    Algoritmo de similitud usando embeddings Sentence-BERT con similitud coseno.
    
    Utiliza modelo all-MiniLM-L6-v2 de Sentence-Transformers para generar
    representaciones semánticas densas de textos y medir similitud.
    
    Attributes:
        name (str): Nombre identificador del algoritmo
        model_name (str): Identificador del modelo en Hugging Face
        model (SentenceTransformer): Modelo cargado de sentence-transformers
    """
    name = "SBERT (coseno)"

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa el algoritmo SBERT con el modelo especificado.
        
        Args:
            model_name (str, optional): Nombre del modelo en Hugging Face.
                                       Default: "sentence-transformers/all-MiniLM-L6-v2"
        
        Notas:
            - all-MiniLM-L6-v2: Modelo ligero (80MB), rápido y efectivo
            - Genera embeddings de 384 dimensiones
            - Optimizado para similitud semántica de oraciones
            - Se descarga automáticamente si no está en caché
        """
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def score(self, a: str, b: str) -> float:
        """
        Calcula similitud semántica entre dos textos usando embeddings SBERT.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Similitud coseno en rango [0, 1]
                  1.0 = textos idénticos/muy similares semánticamente
                  0.0 = textos completamente diferentes
        
        Process:
            1. Genera embeddings normalizados para ambos textos
            2. Calcula similitud coseno: (ea · eb) / (||ea|| · ||eb||)
            3. Retorna score en [0, 1]
        
        Example:
            >>> sbert = SBERTSim()
            >>> sbert.score("machine learning", "artificial intelligence")
            0.78
            >>> sbert.score("cat", "dog")
            0.45
        
        Notas:
            - Embeddings normalizados permiten cálculo eficiente
            - Captura similitud semántica (sinónimos, paráfrasis)
            - No requiere textos del mismo largo
            - Robusto a diferencias de redacción
        """
        from sklearn.metrics.pairwise import cosine_similarity
        ea, eb = self.model.encode([a, b], normalize_embeddings=True)
        return float(cosine_similarity([ea], [eb])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación simple del método de cálculo.
        
        Args:
            a (str): Primer texto (no usado en explicación genérica)
            b (str): Segundo texto (no usado en explicación genérica)
        
        Returns:
            Dict[str, Any]: Diccionario con información del modelo y método
                           - idea: Descripción del método
                           - model: Nombre del modelo usado
        
        Example:
            >>> sbert = SBERTSim()
            >>> sbert.explain("text1", "text2")
            {'idea': 'Embeddings semánticos; coseno', 
             'model': 'sentence-transformers/all-MiniLM-L6-v2'}
        """
        return {"idea": "Embeddings semánticos; coseno", "model": self.model_name}

# ===============================
# GTE – General Text Embeddings
# ===============================
class GTESim(SimilarityAlgorithm):
    """
    Algoritmo de similitud usando embeddings GTE con similitud coseno.
    
    Utiliza modelo GTE (General Text Embeddings) de Alibaba DAMO Academy,
    optimizado para similitud textual de propósito general con alta calidad.
    
    Attributes:
        name (str): Nombre identificador del algoritmo
        model_name (str): Identificador del modelo en Hugging Face
        model (SentenceTransformer): Modelo cargado de sentence-transformers
    
    Ventajas:
        - Modelo de última generación (2023)
        - Mejor desempeño que modelos anteriores en benchmarks
        - Optimizado para textos cortos y resúmenes
        - Gratuito y de código abierto
    """
    name = "GTE (coseno)"

    def __init__(self, model_name: str = "thenlper/gte-small"):
        """
        Inicializa el algoritmo GTE con el modelo especificado.
        
        Args:
            model_name (str, optional): Nombre del modelo en Hugging Face.
                                       Default: "thenlper/gte-small"
        
        Notas:
            - thenlper/gte-small: Modelo de ~33M parámetros
            - Genera embeddings de 384 dimensiones
            - Superior a SBERT en benchmarks MTEB (2023)
            - Entrenado en corpus masivo multilingüe
            - Se descarga automáticamente si no está en caché
        """
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def score(self, a: str, b: str) -> float:
        """
        Calcula similitud semántica entre dos textos usando embeddings GTE.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Similitud coseno en rango [0, 1]
                  1.0 = textos idénticos/muy similares semánticamente
                  0.0 = textos completamente diferentes
        
        Process:
            1. Genera embeddings normalizados para ambos textos con GTE
            2. Calcula similitud coseno: (ea · eb) / (||ea|| · ||eb||)
            3. Retorna score en [0, 1]
        
        Example:
            >>> gte = GTESim()
            >>> gte.score("deep learning models", "neural network architectures")
            0.82
            >>> gte.score("economics", "biology")
            0.15
        
        Notas:
            - GTE típicamente más preciso que SBERT en similitud semántica
            - Excelente para textos académicos y técnicos
            - Robusto a variaciones lingüísticas
            - Captura relaciones conceptuales profundas
        """
        from sklearn.metrics.pairwise import cosine_similarity
        ea, eb = self.model.encode([a, b], normalize_embeddings=True)
        return float(cosine_similarity([ea], [eb])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Retorna explicación detallada del método de cálculo GTE.
        
        Args:
            a (str): Primer texto (no usado en explicación genérica)
            b (str): Segundo texto (no usado en explicación genérica)
        
        Returns:
            Dict[str, Any]: Diccionario con información del modelo y ventajas
                           - idea: Descripción del método
                           - model: Nombre del modelo usado
                           - ventajas: Características distintivas de GTE
        
        Example:
            >>> gte = GTESim()
            >>> info = gte.explain("text1", "text2")
            >>> print(info['ventajas'])
            'Modelo gratuito, rápido y de última generación (2023)...'
        """
        return {
            "idea": "Embeddings semánticos generados con modelo GTE; similitud medida por coseno",
            "model": self.model_name,
            "ventajas": "Modelo gratuito, rápido y de última generación (2023), ideal para textos cortos o resúmenes."
        }
