from __future__ import annotations
from typing import Dict, List, Tuple, Any, Iterable
from pathlib import Path
from collections import defaultdict, Counter
import itertools

import pandas as pd

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB
from requirement_2.preprocessing import Preprocessor

pp = Preprocessor()

def _window_cooccurrence(tokens: List[str], vocab: set[str], window: int = 20) -> Counter[Tuple[str,str]]:
    """Co-ocurrencias de términos de vocab en ventanas deslizantes."""
    c = Counter()
    if not vocab:
        return c
    n = len(tokens)
    for i in range(n):
        if tokens[i] not in vocab: continue
        jmax = min(n, i + window)
        for j in range(i+1, jmax):
            if tokens[j] not in vocab: continue
            a, b = sorted((tokens[i], tokens[j]))
            if a != b:
                c[(a,b)] += 1
    return c

def build_term_graph(
    bib_path: Path = DEFAULT_BIB,
    candidate_terms: Iterable[str] | None = None,
    min_df: int = 3,
    window: int = 30,
    min_cooc: int = 2,
) -> Dict[str, Any]:
    """
    Grafo no dirigido G=(V,E) sobre términos:
      - V: términos
      - E: co-ocurrencias en ventanas (peso = frecuencia de co-ocurrencia)
    Reglas:
      - Si candidate_terms se provee (ej. top términos de Req.3), usa ese vocabulario.
      - Si no, usa tokens filtrando por df >= min_df (document frequency).
    """
    df = load_bib_dataframe(bib_path)
    docs = [pp.tokenize(str(a)) for a in df["abstract"].tolist()]
    # vocabulario
    if candidate_terms:
        vocab = {pp.clean(t) for t in candidate_terms if pp.clean(t)}
    else:
        # DF por token
        df_count = Counter()
        for toks in docs:
            df_count.update(set(toks))
        vocab = {t for t, dfv in df_count.items() if dfv >= min_df}

    # co-ocurrencias
    co = Counter()
    for toks in docs:
        co.update(_window_cooccurrence(toks, vocab, window=window))

    # construir nodos y aristas
    nodes = [{"id": t} for t in sorted(vocab)]
    edges = []
    adj: Dict[str, Dict[str, float]] = {t:{} for t in vocab}
    for (a,b), w in co.items():
        if w >= min_cooc:
            edges.append({"u": a, "v": b, "w": int(w)})
            adj[a][b] = float(1.0 / w)  # costo inverso a co-ocurrencia
            adj[b][a] = float(1.0 / w)

    # grados y componentes conexas (BFS)
    degree = {t: 0 for t in vocab}
    for a,b,_ in edges:
        degree[a] += 1
        degree[b] += 1

    comps: List[List[str]] = []
    seen: set[str] = set()
    for t in vocab:
        if t in seen: continue
        q = [t]; seen.add(t)
        comp = []
        while q:
            u = q.pop()
            comp.append(u)
            for v in adj[u].keys():
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(sorted(comp))

    return {
        "nodes": nodes,
        "edges": edges,
        "adj": adj,
        "degree": degree,
        "components": comps,
        "params": {"min_df": min_df, "window": window, "min_cooc": min_cooc, "vocab_size": len(vocab)}
    }
