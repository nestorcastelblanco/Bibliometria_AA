from __future__ import annotations
from typing import List, Dict, Any, Tuple
from requirement_2.preprocessing import Preprocessor

_pp = Preprocessor()

def extract_auto_terms(texts: List[str], max_terms: int = 15, min_df: int = 2, ngram_range=(1,2)) -> List[str]:
    """
    Extrae hasta max_terms términos informativos usando TF-IDF (sin necesidad de etiquetas).
    Filtra tokens vacíos/stopwords y deja 1-2 gramos.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(
        tokenizer=_pp.tokenize, preprocessor=None, lowercase=False, stop_words=None,
        token_pattern=None, ngram_range=ngram_range, min_df=min_df
    )
    X = vec.fit_transform(texts)
    vocab = {v: k for k, v in vec.vocabulary_.items()}
    # importancia global = media TF-IDF de cada término en el corpus
    import numpy as np
    mean_tfidf = X.mean(axis=0).A1  # array
    items = [(vocab[i], float(w)) for i, w in enumerate(mean_tfidf)]
    # filtros de calidad
    def good(term: str) -> bool:
        # evita tokens demasiado cortos o numéricos
        if len(term) < 3: return False
        if any(ch.isdigit() for ch in term): return False
        return True
    ranked = [t for t in sorted(items, key=lambda x: -x[1]) if good(t[0])]
    top = []
    seen = set()
    for term, _ in ranked:
        if term in seen: continue
        seen.add(term)
        top.append(term)
        if len(top) >= max_terms: break
    return top
