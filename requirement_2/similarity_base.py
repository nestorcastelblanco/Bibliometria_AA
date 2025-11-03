"""
Módulo base de interfaz para algoritmos de similitud textual.

Define clase abstracta base (ABC) que todos los algoritmos de similitud
deben implementar, asegurando interfaz consistente para cálculo y explicación.

Parte del Requerimiento 2: Comparación de algoritmos de similitud textual.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any

class SimilarityAlgorithm(ABC):
    """
    Clase abstracta base para algoritmos de similitud textual.
    
    Define interfaz común que todos los algoritmos de similitud deben implementar:
    - score(): Calcula similitud numérica [0,1]
    - explain(): Provee explicación del cálculo
    - compare(): Método de conveniencia que combina ambos
    
    Attributes:
        name (str): Nombre descriptivo del algoritmo (debe ser sobrescrito)
    
    Uso:
        Todas las clases de algoritmos (Levenshtein, Jaccard, SBERT, etc.)
        heredan de esta clase e implementan score() y explain().
    
    Example:
        >>> class MyAlgorithm(SimilarityAlgorithm):
        ...     name = "My Custom Algorithm"
        ...     def score(self, a: str, b: str) -> float:
        ...         return 0.5  # implementación personalizada
        ...     def explain(self, a: str, b: str) -> Dict[str, Any]:
        ...         return {"method": "custom"}
    
    Notas:
        - Todos los scores deben estar normalizados en [0, 1]
        - 1.0 indica máxima similitud (textos idénticos)
        - 0.0 indica mínima similitud (textos completamente diferentes)
        - explain() provee transparencia sobre el cálculo
    """

    name: str = "abstract-base"

    @abstractmethod
    def score(self, a: str, b: str) -> float:
        """
        Calcula score de similitud entre dos textos.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            float: Score de similitud normalizado en [0, 1]
        
        Raises:
            NotImplementedError: Si no se implementa en subclase
        """
        ...

    @abstractmethod
    def explain(self, a: str, b: str) -> Dict[str, Any]:
        """
        Provee explicación del método de cálculo de similitud.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Dict[str, Any]: Diccionario con detalles del cálculo
                           (fórmula, parámetros, valores intermedios, etc.)
        
        Raises:
            NotImplementedError: Si no se implementa en subclase
        """
        ...

    def compare(self, a: str, b: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula similitud y explicación en una sola llamada.
        
        Método de conveniencia que combina score() y explain() para
        obtener tanto el resultado numérico como su explicación.
        
        Args:
            a (str): Primer texto
            b (str): Segundo texto
        
        Returns:
            Tuple[float, Dict[str, Any]]: (score, explicación)
        
        Example:
            >>> algo = SomeAlgorithm()
            >>> score, explanation = algo.compare("text1", "text2")
            >>> print(f"Similitud: {score:.2f}")
            Similitud: 0.85
            >>> print(explanation)
            {'method': 'cosine', 'details': ...}
        
        Notas:
            - Evita llamadas duplicadas a preprocesamiento
            - Útil para reporting y debugging
            - Implementación por defecto disponible para todas las subclases
        """
        s = self.score(a, b)
        return s, self.explain(a, b)
