from __future__ import annotations
from typing import Dict, Any
from .similarity_base import SimilarityAlgorithm

class SBERTSim(SimilarityAlgorithm):
    """Embeddings Sentence-BERT (all-MiniLM-L6-v2) + coseno."""
    name = "SBERT (coseno)"

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def score(self, a: str, b: str) -> float:
        from sklearn.metrics.pairwise import cosine_similarity
        ea, eb = self.model.encode([a, b], normalize_embeddings=True)
        return float(cosine_similarity([ea], [eb])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        return {"idea": "Embeddings semánticos; coseno", "model": self.model_name}

# ===============================
# GTE – General Text Embeddings
# ===============================
class GTESim(SimilarityAlgorithm):
    """Embeddings con modelo GTE (thenlper/gte-small) de Hugging Face."""
    name = "GTE (coseno)"

    def __init__(self, model_name: str = "thenlper/gte-small"):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def score(self, a: str, b: str) -> float:
        from sklearn.metrics.pairwise import cosine_similarity
        ea, eb = self.model.encode([a, b], normalize_embeddings=True)
        return float(cosine_similarity([ea], [eb])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        return {
            "idea": "Embeddings semánticos generados con modelo GTE; similitud medida por coseno",
            "model": self.model_name,
            "ventajas": "Modelo gratuito, rápido y de última generación (2023), ideal para textos cortos o resúmenes."
        }
