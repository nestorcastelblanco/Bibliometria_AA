from __future__ import annotations
from typing import Dict, Any
from .similarity_base import SimilarityAlgorithm
from .preprocessing import Preprocessor
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

_pp = Preprocessor()

class LevenshteinSim(SimilarityAlgorithm):
    name = "Levenshtein (normalizada)"

    def _dist(self, a: str, b: str) -> int:
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
        a, b = _pp.clean(a), _pp.clean(b)
        if not a and not b: return 1.0
        d = self._dist(a, b)
        L = max(len(a), len(b))
        return 1 - d/L

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        a2, b2 = _pp.clean(a), _pp.clean(b)
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return {"formula": "1 - dist/maxlen", "dist": d, "maxlen": L, "normalized": 1 - (d/L) if L else 1.0}

class DamerauLevenshteinSim(SimilarityAlgorithm):
    name = "Damerau–Levenshtein (normalizada)"

    def _dist(self, a: str, b: str) -> int:
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
        a2, b2 = _pp.clean(a), _pp.clean(b)
        if not a2 and not b2: return 1.0
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return 1 - d/L

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        a2, b2 = _pp.clean(a), _pp.clean(b)
        d = self._dist(a2, b2); L = max(len(a2), len(b2))
        return {"formula": "1 - DL/maxlen", "includes": "transposición", "dist": d,
                "normalized": 1 - (d/L) if L else 1.0}

class JaccardTokens(SimilarityAlgorithm):
    name = "Jaccard (tokens)"

    def score(self, a: str, b: str) -> float:
        A = set(_pp.tokenize(a)); B = set(_pp.tokenize(b))
        if not A and not B: return 1.0
        inter = len(A & B); union = len(A | B)
        return inter/union if union else 0.0

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        A = set(_pp.tokenize(a)); B = set(_pp.tokenize(b))
        return {"formula": "|A∩B|/|A∪B|", "|A|": len(A), "|B|": len(B),
                "inter": len(A & B), "union": len(A | B),
                "shared_tokens": sorted(list(A & B))[:25]}

# requirement_2/classic.py
class CosineTFIDF(SimilarityAlgorithm):
    name = "Coseno (TF-IDF)"

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vec = TfidfVectorizer(
            tokenizer=_pp.tokenize,  # usamos tu tokenizador
            preprocessor=None,       # ya limpias en tokenize
            lowercase=False,         # ya haces lowercase en Preprocessor
            stop_words=None,         # ya filtras stopwords en tokenize
            token_pattern=None       # <- para que no haya warning
        )

    def score(self, a: str, b: str) -> float:
        from sklearn.metrics.pairwise import cosine_similarity
        X = self.vec.fit_transform([a, b])
        return float(cosine_similarity(X[0], X[1])[0, 0])

    def explain(self, a: str, b: str) -> Dict[str, Any]:
        X = self.vec.fit_transform([a, b])
        vocab = {v: k for k, v in self.vec.vocabulary_.items()}
        v0 = X[0].tocoo(); v1 = X[1].tocoo()
        tfidf0 = sorted([(vocab[i], float(w)) for i, w in zip(v0.col, v0.data)], key=lambda x: -x[1])[:10]
        tfidf1 = sorted([(vocab[i], float(w)) for i, w in zip(v1.col, v1.data)], key=lambda x: -x[1])[:10]
        return {"formula": "cos(x,y) sobre TF-IDF", "top_tfidf_a": tfidf0, "top_tfidf_b": tfidf1}
