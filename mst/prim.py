"""
Algoritmo de Prim para el árbol de expansión mínima (técnica voraz).

Se parte de un nodo inicial y en cada paso se agrega la arista más ligera
que conecta un nodo del árbol con uno que todavía no está en él.
Se usa un heap (cola de prioridad) para obtener esa arista rápidamente.

Complejidad: O(E log V).
"""
import heapq


def prim(grafo, inicio=0):
    """Regresa (aristas_del_arbol, peso_total, pasos).

    `pasos` es una lista de (peso, u, v, aceptada): las aristas que salen
    del heap; se rechazan las que llevan a un nodo ya visitado.
    """
    if grafo.num_nodos == 0:
        return [], 0, []

    ady = grafo.adyacencia()
    visitado = [False] * grafo.num_nodos
    arbol = []
    pasos = []
    total = 0

    visitado[inicio] = True
    heap = [(peso, inicio, v) for peso, v in ady[inicio]]
    heapq.heapify(heap)

    while heap and len(arbol) < grafo.num_nodos - 1:
        peso, u, v = heapq.heappop(heap)
        if visitado[v]:
            pasos.append((peso, u, v, False))
            continue
        visitado[v] = True
        arbol.append((peso, u, v))
        total += peso
        pasos.append((peso, u, v, True))
        for peso_sig, w in ady[v]:
            if not visitado[w]:
                heapq.heappush(heap, (peso_sig, v, w))

    return arbol, total, pasos
