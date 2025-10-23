from __future__ import annotations
from requirement_2.preprocessing import Preprocessor

def preprocess_corpus(texts):
    """Limpia y tokeniza cada abstract, devolviendo texto preprocesado."""
    pp = Preprocessor()
    return [pp.clean(t) for t in texts]
    