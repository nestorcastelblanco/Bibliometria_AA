from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any

class SimilarityAlgorithm(ABC):
    """Interfaz común para algoritmos de similitud (score en [0,1] + explicación)."""

    name: str = "abstract-base"

    @abstractmethod
    def score(self, a: str, b: str) -> float: ...

    @abstractmethod
    def explain(self, a: str, b: str) -> Dict[str, Any]: ...

    def compare(self, a: str, b: str) -> Tuple[float, Dict[str, Any]]:
        s = self.score(a, b)
        return s, self.explain(a, b)
