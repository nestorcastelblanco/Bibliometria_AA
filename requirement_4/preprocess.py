"""
Módulo de preprocesamiento de texto para clustering jerárquico.

Aplica limpieza y tokenización a corpus de abstracts bibliométricos
utilizando el Preprocessor del Requerimiento 2.

Parte del Requerimiento 4: Clustering jerárquico y dendrogramas.
"""
from __future__ import annotations
from requirement_2.preprocessing import Preprocessor

def preprocess_corpus(texts):
    """
    Limpia y tokeniza cada abstract, devolviendo texto preprocesado.
    
    Aplica el pipeline completo de Preprocessor del Requerimiento 2:
    - Normalización de caracteres
    - Remoción de stopwords
    - Tokenización
    - Stemming/Lemmatización (según configuración)
    
    Args:
        texts (list): Lista de strings (abstracts) a preprocesar
    
    Returns:
        list: Lista de strings con texto limpio y tokenizado
    
    Example:
        >>> texts = [
        ...     "Machine learning algorithms for data analysis",
        ...     "Deep neural networks in computer vision"
        ... ]
        >>> clean_texts = preprocess_corpus(texts)
        >>> len(clean_texts) == len(texts)
        True
        >>> # Resultado típico: ['machin learn algorithm data analysi', ...]
    
    Notas:
        - Usa Preprocessor del requirement_2 para consistencia
        - Cada abstract se procesa independientemente
        - Resultado es texto limpio listo para vectorización TF-IDF
        - Preprocesamiento crítico para calidad de clustering
    """
    pp = Preprocessor()
    return [pp.clean(t) for t in texts]
    