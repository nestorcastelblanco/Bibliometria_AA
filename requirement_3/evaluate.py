from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional

# Intentamos usar GTE; si no, SBERT
def _load_embedder():
    from sentence_transformers import SentenceTransformer
    try:
        return SentenceTransformer("thenlper/gte-small"), "thenlper/gte-small"
    except Exception:
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"), "sentence-transformers/all-MiniLM-L6-v2"

def precision_against_seeds(auto_terms: List[str], seed_terms: List[str], threshold: float = 0.50) -> Dict[str, Any]:
    """
    Calcula precisión de los términos auto-generados vs. semillas usando similitud por coseno de embeddings.
    Marca un término como 'relevante' si la similitud con alguna semilla >= threshold.
    """
    from sklearn.metrics.pairwise import cosine_similarity
    model, model_name = _load_embedder()
    # Embeddings (normalizados)
    seed_emb = model.encode(seed_terms, normalize_embeddings=True)
    auto_emb = model.encode(auto_terms, normalize_embeddings=True)
    M = cosine_similarity(auto_emb, seed_emb)  # [len(auto), len(seeds)]
    per_term = []
    hits = 0
    for i, term in enumerate(auto_terms):
        best = float(M[i].max()) if M.shape[1] else 0.0
        ok = best >= threshold
        if ok: hits += 1
        per_term.append({"term": term, "max_sim": best, "relevant": ok})
    prec = hits / len(auto_terms) if auto_terms else 0.0
    return {
        "model": model_name,
        "threshold": threshold,
        "precision": prec,
        "details": per_term
    }
