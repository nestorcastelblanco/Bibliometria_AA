"""
Módulo de evaluación de términos usando embeddings semánticos.

Funcionalidades:
- Carga de modelos de embeddings (GTE o SBERT como fallback)
- Cálculo de similitud semántica coseno entre términos
- Evaluación de precisión de términos auto-generados vs términos semilla
- Análisis de relevancia basado en umbral de similitud

Parte del Requerimiento 3: Evaluación de calidad de términos automáticos.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional

def _load_embedder():
    """
    Carga modelo de embeddings de sentence-transformers con estrategia de fallback.
    
    Intenta cargar modelo GTE (alta calidad) primero, si falla usa
    all-MiniLM-L6-v2 (más ligero y compatible).
    
    Returns:
        Tuple[SentenceTransformer, str]: Modelo cargado y nombre del modelo
    
    Modelos intentados (en orden):
        1. thenlper/gte-small: Modelo GTE optimizado (preferido)
        2. sentence-transformers/all-MiniLM-L6-v2: Fallback ligero y rápido
    
    Example:
        >>> model, name = _load_embedder()
        >>> print(name)
        'thenlper/gte-small'
    
    Notas:
        - GTE (General Text Embeddings) ofrece mejor calidad semántica
        - all-MiniLM-L6-v2 es fallback confiable y rápido
        - Ambos modelos soportan normalización de embeddings
        - Modelos se descargan automáticamente si no están en caché
    """
    from sentence_transformers import SentenceTransformer
    try:
        return SentenceTransformer("thenlper/gte-small"), "thenlper/gte-small"
    except Exception:
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"), "sentence-transformers/all-MiniLM-L6-v2"

def precision_against_seeds(auto_terms: List[str], seed_terms: List[str], threshold: float = 0.50) -> Dict[str, Any]:
    """
    Calcula precisión de términos auto-generados comparándolos con términos semilla.
    
    Evalúa la calidad de términos extraídos automáticamente calculando similitud
    semántica con términos semilla (ground truth) usando embeddings de sentence-transformers.
    Un término se considera relevante si su similitud máxima con cualquier semilla
    supera el umbral especificado.
    
    Args:
        auto_terms (List[str]): Términos generados automáticamente (TF-IDF, etc)
        seed_terms (List[str]): Términos semilla de referencia (ground truth)
        threshold (float, optional): Umbral de similitud coseno [0,1]. Default: 0.50
    
    Returns:
        Dict[str, Any]: Diccionario con resultados de evaluación:
            - model (str): Nombre del modelo de embeddings usado
            - threshold (float): Umbral aplicado
            - precision (float): Precisión global [0,1]
            - details (List[Dict]): Detalle por término:
                - term (str): Término evaluado
                - max_sim (float): Similitud máxima con semillas
                - relevant (bool): Si supera umbral
    
    Process:
        1. Carga modelo de embeddings (GTE o MiniLM)
        2. Genera embeddings normalizados para ambos conjuntos
        3. Calcula matriz de similitud coseno [len(auto) x len(seeds)]
        4. Por cada término auto, encuentra máxima similitud con semillas
        5. Marca como relevante si max_sim >= threshold
        6. Calcula precisión = hits / total_auto_terms
    
    Example:
        >>> auto = ["neural networks", "deep learning", "random text"]
        >>> seeds = ["machine learning", "neural network", "ai models"]
        >>> result = precision_against_seeds(auto, seeds, threshold=0.70)
        >>> result['precision']
        0.6667  # 2 de 3 términos relevantes
        >>> result['details'][0]
        {'term': 'neural networks', 'max_sim': 0.95, 'relevant': True}
    
    Métricas:
        - Precision = (términos relevantes) / (total términos auto)
        - Relevante = max(similitud con semillas) >= threshold
        - Similitud coseno normalizada: rango [0, 1]
    
    Notas:
        - Usa embeddings normalizados para similitud coseno eficiente
        - No requiere coincidencia exacta de strings (captura sinonimia)
        - Threshold típicos: 0.50 (permisivo), 0.70 (balanceado), 0.85 (estricto)
        - Útil para validar descubrimiento automático de términos
        - Complementa métricas de frecuencia con evaluación semántica
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
