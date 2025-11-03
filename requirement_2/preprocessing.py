"""
Módulo de preprocesamiento de texto para análisis de similitud.

Implementa limpieza y tokenización configurable de textos con:
- Normalización de mayúsculas/minúsculas
- Eliminación de puntuación y números
- Filtrado de stopwords en inglés
- Tokenización basada en espacios

Parte del Requerimiento 2: Preprocesamiento para algoritmos de similitud textual.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import List, Iterable

_STOPWORDS = set(
    """
    a about above after again against all am an and any are aren't as at be because been
    before being below between both but by can't cannot could couldn't did didn't do does
    doesn't doing don't down during each few for from further had hadn't has hasn't have
    haven't having he he'd he'll he's her here here's hers herself him himself his how
    how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me more most
    mustn't my myself no nor not of off on once only or other ought our ours ourselves
    out over own same shan't she she'd she'll she's should shouldn't so some such than
    that that's the their theirs them themselves then there there's these they they'd
    they'll they're they've this those through to too under until up very was wasn't we
    we'd we'll we're we've were weren't what what's when when's where where's which while
    who who's whom why why's with won't would wouldn't you you'd you'll you're you've your
    yours yourself yourselves
    """.split()
)
"""
Set[str]: Lista de stopwords comunes en inglés.

Incluye 174 palabras funcionales que típicamente no aportan significado
semántico relevante: artículos, preposiciones, pronombres, auxiliares, etc.

Basado en lista estándar de NLTK/spaCy con contracciones incluidas.
"""

@dataclass
class Preprocessor:
    """
    Preprocesador configurable de texto para análisis de similitud.
    
    Provee pipeline de limpieza y tokenización con opciones configurables
    para normalización, eliminación de puntuación, números y stopwords.
    
    Attributes:
        lowercase (bool): Si True, convierte texto a minúsculas. Default: True
        rm_punct (bool): Si True, elimina puntuación. Default: True
        rm_numbers (bool): Si True, elimina números. Default: True
        stopwords (Iterable[str]): Set de stopwords a filtrar. Default: _STOPWORDS
    
    Example:
        >>> pp = Preprocessor(lowercase=True, rm_numbers=True)
        >>> pp.clean("Machine Learning 2024!")
        'machine learning'
        >>> pp.tokenize("The quick brown fox")
        ['quick', 'brown', 'fox']  # sin 'the'
    
    Notas:
        - Todos los algoritmos de similitud deben usar mismo preprocesador
        - Configuración por defecto optimizada para textos académicos
        - Soporta caracteres Unicode (útil para acentos y caracteres especiales)
        - Tokenización simple por espacios después de limpieza
    """
    lowercase: bool = True
    rm_punct: bool = True
    rm_numbers: bool = True
    stopwords: Iterable[str] = None

    def __post_init__(self):
        """
        Inicialización post-dataclass para configurar stopwords por defecto.
        
        Ejecutado automáticamente después de __init__ por el decorador @dataclass.
        Asigna _STOPWORDS si no se proveyó lista personalizada.
        """
        if self.stopwords is None:
            self.stopwords = _STOPWORDS

    def clean(self, text: str) -> str:
        """
        Limpia y normaliza texto según configuración del preprocesador.
        
        Aplica secuencialmente las transformaciones configuradas:
        minúsculas, eliminación de números, eliminación de puntuación,
        normalización de espacios.
        
        Args:
            text (str): Texto a limpiar
        
        Returns:
            str: Texto limpio y normalizado
        
        Process:
            1. Si text es None, retorna string vacío
            2. Si lowercase=True: convierte a minúsculas
            3. Si rm_numbers=True: elimina dígitos con regex
            4. Si rm_punct=True: elimina puntuación con regex Unicode
            5. Normaliza espacios múltiples a uno solo
            6. Elimina espacios al inicio y final
        
        Example:
            >>> pp = Preprocessor()
            >>> pp.clean("Machine Learning 2024!")
            'machine learning'
            >>> pp.clean("  Text  with   spaces  ")
            'text with spaces'
            >>> pp.clean(None)
            ''
        
        Notas:
            - Regex [^\w\s] preserva letras, dígitos (si enabled) y espacios
            - Flag re.UNICODE soporta caracteres acentuados y no-ASCII
            - Orden de operaciones importante para resultado consistente
            - No modifica texto original (inmutable)
        """
        if text is None:
            return ""
        t = text
        if self.lowercase:
            t = t.lower()
        if self.rm_numbers:
            t = re.sub(r"\d+", " ", t)
        if self.rm_punct:
            # elimina todo lo que no sea letra/dígito/espacio (Unicode)
            t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto en lista de palabras sin stopwords.
        
        Combina limpieza (clean()) y tokenización por espacios con
        filtrado de stopwords para obtener tokens significativos.
        
        Args:
            text (str): Texto a tokenizar
        
        Returns:
            List[str]: Lista de tokens (palabras) sin stopwords
        
        Process:
            1. Limpia texto con clean() (normalización completa)
            2. Divide por espacios en blanco
            3. Filtra palabras que están en self.stopwords
            4. Retorna lista de tokens resultantes
        
        Example:
            >>> pp = Preprocessor()
            >>> pp.tokenize("The Machine Learning models are powerful")
            ['machine', 'learning', 'models', 'powerful']
            >>> pp.tokenize("An introduction to AI")
            ['introduction', 'ai']
        
        Notas:
            - Stopwords eliminan palabras funcionales sin significado
            - Útil para TF-IDF, Jaccard y análisis de frecuencias
            - Orden de palabras se preserva (no es set)
            - Puede retornar lista vacía si todo son stopwords
            - Consistente con limpieza aplicada en clean()
        """
        t = self.clean(text)
        return [w for w in t.split() if w not in self.stopwords]
