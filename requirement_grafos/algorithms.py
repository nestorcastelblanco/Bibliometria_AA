from __future__ import annotations
from typing import Dict, List, Tuple, Any
import math
from collections import defaultdict, deque

Graph = Dict[str, Dict[str, float]]  # adj[u][v] = peso (distancia o 1-sim)

def dijkstra(adj: Graph, src: str) -> Tuple[Dict[str, float], Dict[str, str | None]]:
    dist = {u: math.inf for u in adj}
    prev = {u: None for u in adj}
    dist[src] = 0.0
    visited: set[str] = set()
    while len(visited) < len(adj):
        # escoger el no visitado con menor dist
        u = min((n for n in adj if n not in visited), key=lambda x: dist[x], default=None)
        if u is None or dist[u] == math.inf:
            break
        visited.add(u)
        for v, w in adj[u].items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
    return dist, prev

def reconstruct_path(prev: Dict[str, str | None], src: str, tgt: str) -> List[str]:
    if prev.get(tgt) is None and src != tgt:
        return []
    path = [tgt]
    while path[-1] != src:
        p = prev[path[-1]]
        if p is None: return []
        path.append(p)
    path.reverse()
    return path

def floyd_warshall(adj: Graph) -> Tuple[Dict[Tuple[str,str], float], Dict[Tuple[str,str], str | None]]:
    nodes = list(adj.keys())
    dist: Dict[Tuple[str,str], float] = {}
    nxt: Dict[Tuple[str,str], str | None] = {}
    for i in nodes:
        for j in nodes:
            if i == j:
                dist[(i,j)] = 0.0
                nxt[(i,j)] = None
            elif j in adj[i]:
                dist[(i,j)] = adj[i][j]
                nxt[(i,j)] = j
            else:
                dist[(i,j)] = math.inf
                nxt[(i,j)] = None
    for k in nodes:
        for i in nodes:
            dik = dist[(i,k)]
            if dik == math.inf: continue
            for j in nodes:
                nk = dist[(k,j)]
                if nk == math.inf: continue
                nd = dik + nk
                if nd < dist[(i,j)]:
                    dist[(i,j)] = nd
                    nxt[(i,j)] = nxt[(i,k)]
    return dist, nxt

def fw_path(nxt: Dict[Tuple[str,str], str | None], i: str, j: str) -> List[str]:
    if nxt[(i,j)] is None:
        return [i] if i == j else []
    path = [i]
    while i != j:
        i = nxt[(i,j)]  # type: ignore
        if i is None: return []
        path.append(i)
    return path

def strongly_connected_components(adj: Graph) -> List[List[str]]:
    # Kosaraju
    sys_nodes = list(adj.keys())
    # construir transpuesto
    tr: Graph = {u:{} for u in sys_nodes}
    for u in adj:
        for v in adj[u]:
            tr.setdefault(v, {})
            tr[v][u] = adj[u][v]

    visited: set[str] = set()
    order: List[str] = []

    def dfs1(u: str):
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                dfs1(v)
        order.append(u)

    for u in sys_nodes:
        if u not in visited:
            dfs1(u)

    comps: List[List[str]] = []
    visited.clear()

    def dfs2(u: str, comp: List[str]):
        visited.add(u)
        comp.append(u)
        for v in tr[u]:
            if v not in visited:
                dfs2(v, comp)

    for u in reversed(order):
        if u not in visited:
            comp: List[str] = []
            dfs2(u, comp)
            comps.append(comp)
    return comps
