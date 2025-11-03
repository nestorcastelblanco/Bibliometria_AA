"""
Módulo para cálculo de matrices de similitud y distancia entre documentos.

Implementa vectorización TF-IDF y similitud coseno para medir proximidad
semántica entre abstracts. Convierte similitudes a distancias para clustering.

Parte del Requerimiento 4: Clustering jerárquico y dendrogramas.
"""
from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_similarity_matrix(texts):
    """
    Crea matriz de similitud coseno entre abstracts usando TF-IDF.
    
    Proceso de 4 pasos:
    1. Vectoriza textos con TF-IDF (stop_words='english')
    2. Calcula similitud coseno pareada (range [0,1])
    3. Asegura diagonal = 1.0 (similitud consigo mismo)
    4. Retorna matriz cuadrada simétrica
    
    Args:
        texts (list): Lista de strings con texto preprocesado
    
    Returns:
        np.ndarray: Matriz NxN donde sim[i,j] ∈ [0,1] es similitud entre textos i,j
    
    Example:
        >>> texts = ["machine learning", "deep learning", "data science"]
        >>> sim = build_similarity_matrix(texts)
        >>> sim.shape
        (3, 3)
        >>> sim[0, 0]  # Auto-similitud
        1.0
        >>> 0 <= sim[0, 1] <= 1  # Similitud entre pares
        True
    
    TF-IDF (Term Frequency - Inverse Document Frequency):
        - TF: Frecuencia del término en documento
        - IDF: Penaliza términos muy comunes en corpus
        - Vector sparse de alta dimensión (vocabulario)
    
    Similitud Coseno:
        - cos(θ) = (A·B) / (||A|| ||B||)
        - 1.0 = vectores idénticos
        - 0.0 = ortogonales (sin términos compartidos)
        - Invariante a longitud del documento
    
    Notas:
        - stop_words='english' elimina palabras comunes (the, is, and...)
        - Resultado es matriz simétrica: sim[i,j] = sim[j,i]
        - Valores en [0, 1] por definición del coseno normalizado
        - Útil para identificar abstracts temáticamente similares
    """
    # PASO 1: Vectorización TF-IDF
    vec = TfidfVectorizer(stop_words='english')
    X = vec.fit_transform(texts)
    
    # PASO 2: Similitud coseno entre todos los pares
    sim = cosine_similarity(X)
    
    # PASO 3: Asegurar diagonal = 1.0 (corrección numérica)
    np.fill_diagonal(sim, 1.0)
    
    # PASO 4: Retornar matriz
    return sim

def similarity_to_distance(sim_matrix):
    """
    Convierte matriz de similitud a matriz de distancia.
    
    Transforma similitud coseno [0,1] en métrica de distancia [0,1]
    usando la relación: distancia = 1 - similitud
    
    Args:
        sim_matrix (np.ndarray): Matriz NxN de similitudes en [0,1]
    
    Returns:
        np.ndarray: Matriz NxN de distancias en [0,1]
    
    Example:
        >>> sim = np.array([[1.0, 0.8], [0.8, 1.0]])
        >>> dist = similarity_to_distance(sim)
        >>> dist
        array([[0. , 0.2],
               [0.2, 0. ]])
    
    Interpretación:
        - dist[i,j] = 0 → documentos idénticos (sim = 1.0)
        - dist[i,j] = 1 → documentos completamente distintos (sim = 0.0)
        - dist[i,j] pequeño → alta similitud semántica
        - dist[i,j] grande → baja similitud semántica
    
    Propiedades:
        - Resultado es métrica válida (simétrica, no-negativa)
        - Diagonal = 0 (distancia consigo mismo)
        - Compatible con clustering jerárquico (scipy.cluster.hierarchy)
    
    Notas:
        - Conversión estándar para algoritmos de clustering
        - scipy.cluster espera distancias, no similitudes
        - Mantiene relaciones: sim alta → dist baja, sim baja → dist alta
    """
    return 1 - sim_matrix
