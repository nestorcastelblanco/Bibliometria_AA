from __future__ import annotations
from typing import List, Dict, Any, Iterable
from collections import Counter
from requirement_2.preprocessing import Preprocessor

_pp = Preprocessor()

def normalize_terms(terms: Iterable[str]) -> List[str]:
    # Normaliza términos (minúsculas y limpieza light para matcheo robusto)
    norm = []
    for t in terms:
        x = _pp.clean(t)
        norm.append(x)
    return norm

def term_frequencies_per_doc(texts: List[str], terms: List[str]) -> List[Dict[str, int]]:
    """Cuenta apariciones por documento (sobre tokens) para cada término (1-2 palabras)."""
    # tokenizamos cada doc
    tokenized = [ _pp.tokenize(t) for t in texts ]
    # map de términos -> listas de tokens del término
    term_tokens = {term: term.split() for term in terms}
    per_doc = []
    for toks in tokenized:
        c = Counter()
        # índice para buscar n-gramas 1-2
        unigrams = toks
        bigrams = [" ".join(pair) for pair in zip(toks, toks[1:])]
        bag = Counter(unigrams) + Counter(bigrams)
        for term, tt in term_tokens.items():
            key = " ".join(tt)
            c[term] = bag.get(key, 0)
        per_doc.append(dict(c))
    return per_doc

def aggregate_frequencies(per_doc: List[Dict[str,int]]) -> Dict[str, int]:
    agg = Counter()
    for d in per_doc:
        agg.update(d)
    return dict(agg)
