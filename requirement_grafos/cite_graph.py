from __future__ import annotations
from typing import Dict, List, Any, Tuple
from pathlib import Path
import math

import pandas as pd

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB
from requirement_2.preprocessing import Preprocessor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

pp = Preprocessor()

def _int_year(y: Any) -> int | None:
    try:
        i = int(str(y)[:4])
        if 1800 <= i <= 2100: return i
    except Exception:
        return None
    return None

def build_citation_graph(
    bib_path: Path = DEFAULT_BIB,
    min_sim: float = 0.35,
    use_explicit: bool = True
) -> Dict[str, Any]:
    """
    Devuelve:
      {
        'nodes': [{'id': 'A0', 'title': ..., 'year': ...}, ...],
        'edges': [{'u':'A0','v':'A5','w':0.6}, ...],       # dirigido u -> v
        'adj':   {'A0': {'A5': 1-w, ...}, ...}            # pesos como 'costo' = 1-sim
      }
    Reglas:
      - Si existen campos de referencia explícita (no usuales en BibTeX sin scraping), úsalos.
      - Si no, infiere aristas: similitud TF-IDF entre (title + keywords + authors)
        y dirección por año (del más nuevo al más antiguo). Si no hay año, por índice.
    """
    df = load_bib_dataframe(bib_path)
    # preparar texto para similitud
    cols = ["title", "keywords", "authors"]
    texts = []
    for i, r in df.iterrows():
        chunk = " ".join(str(r.get(c, "")) for c in cols)
        texts.append(pp.clean(chunk))

    # TF-IDF y similitud
    vec = TfidfVectorizer()
    X = vec.fit_transform(texts)
    S = cosine_similarity(X)
    n = len(df)
    nodes = []
    for i in range(n):
        nodes.append({
            "id": f"A{i}",
            "title": str(df.iloc[i].get("title","")),
            "year": _int_year(df.iloc[i].get("year","")),
            "journal": str(df.iloc[i].get("journal","")),
        })

    edges = []
    adj: Dict[str, Dict[str, float]] = {f"A{i}": {} for i in range(n)}

    # Inferencia de aristas dirigidas por año (más nuevo cita a más antiguo)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            sim = float(S[i, j])
            if sim >= min_sim:
                ai, aj = nodes[i], nodes[j]
                yi, yj = ai["year"], aj["year"]
                if yi is not None and yj is not None and yi != yj:
                    # más nuevo -> más antiguo
                    u, v = (f"A{i}", f"A{j}") if yi > yj else (f"A{j}", f"A{i}")
                else:
                    # sin año: usa índice para dirección estable
                    u, v = (f"A{i}", f"A{j}") if i > j else (f"A{j}", f"A{i}")
                w_sim = sim
                w_cost = 1.0 - w_sim
                # evita multi-aristas u->v
                if v not in adj[u]:
                    edges.append({"u": u, "v": v, "w": round(w_sim, 4)})
                    adj[u][v] = round(w_cost, 6)

    return {"nodes": nodes, "edges": edges, "adj": adj}
