"""
Módulo de algoritmos de teoría de grafos para análisis bibliométrico.

Implementa algoritmos clásicos para encontrar caminos más cortos y 
componentes fuertemente conexas en grafos dirigidos y no dirigidos.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any
import math
from collections import defaultdict, deque

# Tipo alias para representación de grafos mediante lista de adyacencia
# adj[u][v] = peso/costo de la arista u→v
Graph = Dict[str, Dict[str, float]]

def dijkstra(adj: Graph, src: str) -> Tuple[Dict[str, float], Dict[str, str | None]]:
    """
    Algoritmo de Dijkstra para encontrar caminos más cortos desde un nodo origen.
    
    Encuentra el camino de menor costo desde el nodo origen (src) a todos los
    demás nodos alcanzables en el grafo. Es óptimo para grafos con pesos no negativos.
    
    Complejidad: O(V²) donde V es el número de vértices
    (podría optimizarse a O((V+E)logV) con heap de prioridad)
    
    Args:
        adj (Graph): Grafo representado como diccionario de adyacencia
                    {nodo: {vecino: costo}}
        src (str): Identificador del nodo origen
    
    Returns:
        Tuple[Dict[str, float], Dict[str, str | None]]:
            - dist: Diccionario {nodo: distancia_mínima_desde_src}
            - prev: Diccionario {nodo: nodo_previo_en_camino_óptimo}
    
    Ejemplo:
        >>> adj = {'A': {'B': 1.0, 'C': 4.0}, 'B': {'C': 2.0}, 'C': {}}
        >>> dist, prev = dijkstra(adj, 'A')
        >>> dist['C']  # Distancia de A a C
        3.0
        >>> prev['C']  # Nodo previo a C en el camino óptimo
        'B'
    
    Notas:
        - Los nodos no alcanzables desde src tendrán dist = inf
        - El nodo origen tiene dist[src] = 0
        - prev[src] = None (no hay nodo previo al origen)
    """
    # Inicializar distancias a infinito y predecesores a None
    dist = {u: math.inf for u in adj}
    prev = {u: None for u in adj}
    dist[src] = 0.0
    visited: set[str] = set()
    
    # Iterar hasta visitar todos los nodos
    while len(visited) < len(adj):
        # Seleccionar nodo no visitado con menor distancia (cola de prioridad greedy)
        u = min(
            (n for n in adj if n not in visited), 
            key=lambda x: dist[x], 
            default=None
        )
        
        # Si no hay más nodos alcanzables, terminar
        if u is None or dist[u] == math.inf:
            break
        
        visited.add(u)
        
        # Relajación: actualizar distancias de vecinos de u
        for v, w in adj[u].items():
            # Si encontramos un camino más corto a v pasando por u
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
    
    return dist, prev

def reconstruct_path(prev: Dict[str, str | None], src: str, tgt: str) -> List[str]:
    """
    Reconstruye el camino desde origen a destino usando el diccionario de predecesores.
    
    Utiliza el diccionario 'prev' generado por Dijkstra para reconstruir la
    secuencia de nodos que forma el camino más corto desde src hasta tgt.
    
    Args:
        prev (Dict[str, str | None]): Diccionario de predecesores {nodo: nodo_previo}
        src (str): Identificador del nodo origen
        tgt (str): Identificador del nodo destino
    
    Returns:
        List[str]: Lista ordenada de nodos desde src hasta tgt
                  Lista vacía si no existe camino
    
    Ejemplo:
        >>> prev = {'A': None, 'B': 'A', 'C': 'B'}
        >>> reconstruct_path(prev, 'A', 'C')
        ['A', 'B', 'C']
        >>> reconstruct_path(prev, 'A', 'D')  # D no alcanzable
        []
    
    Algoritmo:
        1. Empieza desde el destino
        2. Retrocede siguiendo los predecesores hasta llegar al origen
        3. Invierte la lista para obtener el orden correcto
    """
    # Si el destino no tiene predecesor y no es el origen, no hay camino
    if prev.get(tgt) is None and src != tgt:
        return []
    
    # Construir camino desde destino hacia origen
    path = [tgt]
    while path[-1] != src:
        p = prev[path[-1]]
        if p is None: 
            return []  # Camino interrumpido
        path.append(p)
    
    # Invertir para tener orden origen→destino
    path.reverse()
    return path

def floyd_warshall(adj: Graph) -> Tuple[Dict[Tuple[str,str], float], Dict[Tuple[str,str], str | None]]:
    """
    Algoritmo de Floyd-Warshall para encontrar todos los caminos más cortos.
    
    Calcula la distancia mínima entre TODOS los pares de nodos del grafo usando
    programación dinámica. Es útil cuando se necesitan muchas consultas de caminos
    o cuando se requiere la matriz completa de distancias.
    
    Complejidad: O(V³) donde V es el número de vértices
    
    Args:
        adj (Graph): Grafo representado como diccionario de adyacencia
    
    Returns:
        Tuple[Dict[Tuple[str,str], float], Dict[Tuple[str,str], str | None]]:
            - dist: Diccionario {(nodo_i, nodo_j): distancia_mínima}
            - nxt: Diccionario {(nodo_i, nodo_j): siguiente_nodo_en_camino}
    
    Ejemplo:
        >>> adj = {'A': {'B': 1.0}, 'B': {'C': 2.0}, 'C': {}}
        >>> dist, nxt = floyd_warshall(adj)
        >>> dist[('A', 'C')]  # Distancia de A a C
        3.0
        >>> nxt[('A', 'C')]  # Siguiente nodo desde A hacia C
        'B'
    
    Algoritmo:
        Para cada nodo intermedio k:
            Para cada par de nodos (i, j):
                Si el camino i→k→j es más corto que i→j directo:
                    Actualizar dist[i,j] y nxt[i,j]
    
    Notas:
        - Funciona con grafos dirigidos y no dirigidos
        - Puede detectar ciclos negativos (no aplicable aquí)
        - dist[(i,i)] = 0 para todo nodo i
        - dist[(i,j)] = inf si no hay camino de i a j
    """
    nodes = list(adj.keys())
    dist: Dict[Tuple[str,str], float] = {}
    nxt: Dict[Tuple[str,str], str | None] = {}
    
    # === INICIALIZACIÓN ===
    # Establecer distancias iniciales basadas en aristas directas
    for i in nodes:
        for j in nodes:
            if i == j:
                # Distancia de un nodo a sí mismo es 0
                dist[(i, j)] = 0.0
                nxt[(i, j)] = None
            elif j in adj[i]:
                # Existe arista directa i→j
                dist[(i, j)] = adj[i][j]
                nxt[(i, j)] = j  # Siguiente nodo es j mismo
            else:
                # No existe arista directa
                dist[(i, j)] = math.inf
                nxt[(i, j)] = None
    
    # === PROGRAMACIÓN DINÁMICA ===
    # Probar cada nodo k como posible nodo intermedio
    for k in nodes:
        for i in nodes:
            dik = dist[(i, k)]
            if dik == math.inf: 
                continue  # No hay camino i→k, saltar
            
            for j in nodes:
                nk = dist[(k, j)]
                if nk == math.inf: 
                    continue  # No hay camino k→j, saltar
                
                # Calcular distancia del camino i→k→j
                nd = dik + nk
                
                # Si este camino es mejor que el actual i→j
                if nd < dist[(i, j)]:
                    dist[(i, j)] = nd
                    # El siguiente nodo desde i hacia j es el mismo que i→k
                    nxt[(i, j)] = nxt[(i, k)]
    
    return dist, nxt

def fw_path(nxt: Dict[Tuple[str,str], str | None], i: str, j: str) -> List[str]:
    """
    Reconstruye el camino entre dos nodos usando el diccionario de Floyd-Warshall.
    
    Utiliza el diccionario 'nxt' generado por floyd_warshall() para reconstruir
    el camino más corto desde el nodo i hasta el nodo j.
    
    Args:
        nxt (Dict[Tuple[str,str], str | None]): Diccionario de siguientes nodos
                                                {(origen, destino): siguiente_nodo}
        i (str): Identificador del nodo origen
        j (str): Identificador del nodo destino
    
    Returns:
        List[str]: Lista ordenada de nodos desde i hasta j
                  Lista vacía si no existe camino
                  Lista [i] si i == j
    
    Ejemplo:
        >>> # Después de ejecutar floyd_warshall(adj)
        >>> nxt = {('A','B'): 'B', ('A','C'): 'B', ('B','C'): 'C'}
        >>> fw_path(nxt, 'A', 'C')
        ['A', 'B', 'C']
        >>> fw_path(nxt, 'A', 'A')
        ['A']
    
    Algoritmo:
        1. Si nxt[(i,j)] es None: no hay camino (o i==j)
        2. Empezar desde i y seguir los "siguientes nodos" hasta llegar a j
        3. Cada paso: i = nxt[(i,j)] nos acerca a j
    """
    # Caso especial: si no hay siguiente nodo
    if nxt[(i, j)] is None:
        return [i] if i == j else []  # Solo retorna [i] si es el mismo nodo
    
    # Construir camino siguiendo los "siguientes nodos"
    path = [i]
    while i != j:
        i = nxt[(i, j)]  # type: ignore
        if i is None: 
            return []  # Camino interrumpido
        path.append(i)
    
    return path

def strongly_connected_components(adj: Graph) -> List[List[str]]:
    """
    Algoritmo de Kosaraju para encontrar componentes fuertemente conexas (SCC).
    
    Una componente fuertemente conexa es un subconjunto maximal de nodos donde
    existe un camino dirigido entre cada par de nodos en ambas direcciones.
    En grafos de citaciones, una SCC indica un grupo de artículos que se citan
    mutuamente (ciclos de citación).
    
    Complejidad: O(V + E) donde V = vértices, E = aristas
    
    Args:
        adj (Graph): Grafo dirigido representado como diccionario de adyacencia
    
    Returns:
        List[List[str]]: Lista de componentes, cada una es una lista de nodos
                        Ordenadas por tamaño decreciente implícitamente
    
    Ejemplo:
        >>> adj = {
        ...     'A': {'B': 1.0},
        ...     'B': {'C': 1.0},
        ...     'C': {'A': 1.0, 'D': 1.0},
        ...     'D': {}
        ... }
        >>> comps = strongly_connected_components(adj)
        >>> comps
        [['A', 'B', 'C'], ['D']]  # A,B,C forman un ciclo; D está aislado
    
    Algoritmo de Kosaraju (dos pasadas de DFS):
        1. Primera DFS en el grafo original: registrar orden de finalización
        2. Construir grafo transpuesto (invertir todas las aristas)
        3. Segunda DFS en el grafo transpuesto siguiendo orden inverso
        4. Cada árbol DFS de la segunda pasada es una SCC
    
    Notas:
        - En grafos de citaciones sin ciclos, cada nodo es su propia SCC
        - SCCs grandes indican grupos de papers que se referencian mutuamente
        - El algoritmo funciona solo en grafos dirigidos
    """
    sys_nodes = list(adj.keys())
    
    # === PASO 1: Construir grafo transpuesto (invertir aristas) ===
    # En el transpuesto: si existe u→v en original, existe v→u en transpuesto
    tr: Graph = {u: {} for u in sys_nodes}
    for u in adj:
        for v in adj[u]:
            tr.setdefault(v, {})
            tr[v][u] = adj[u][v]  # Invertir la arista

    # === PASO 2: Primera DFS en grafo original ===
    # Objetivo: determinar orden de finalización de nodos
    visited: set[str] = set()
    order: List[str] = []  # Orden en que terminan los nodos (post-orden)

    def dfs1(u: str):
        """DFS que registra nodos en orden de finalización."""
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                dfs1(v)
        # Al terminar de explorar u, agregarlo al orden
        order.append(u)

    # Ejecutar DFS desde cada nodo no visitado
    for u in sys_nodes:
        if u not in visited:
            dfs1(u)

    # === PASO 3: Segunda DFS en grafo transpuesto ===
    # Objetivo: encontrar componentes conexas en el transpuesto
    comps: List[List[str]] = []
    visited.clear()

    def dfs2(u: str, comp: List[str]):
        """DFS que construye una componente fuertemente conexa."""
        visited.add(u)
        comp.append(u)
        # Explorar vecinos en el grafo transpuesto
        for v in tr[u]:
            if v not in visited:
                dfs2(v, comp)

    # Procesar nodos en orden inverso de finalización
    for u in reversed(order):
        if u not in visited:
            comp: List[str] = []
            dfs2(u, comp)
            # Cada ejecución de dfs2 encuentra una SCC completa
            comps.append(comp)
    
    return comps
