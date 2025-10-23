from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_similarity_matrix(texts):
    """Crea matriz de similitud coseno entre abstracts."""
    vec = TfidfVectorizer(stop_words='english')
    X = vec.fit_transform(texts)
    sim = cosine_similarity(X)
    np.fill_diagonal(sim, 1.0)
    return sim

def similarity_to_distance(sim_matrix):
    """Convierte similitud [0,1] a distancia [0,1]."""
    return 1 - sim_matrix
