"""
Algoritmo de Kruskal para el árbol de expansión mínima (técnica voraz).

Se ordenan TODAS las aristas por peso y se van tomando de la más ligera
a la más pesada; una arista se acepta solo si no forma ciclo (se revisa
con la estructura Union-Find). Termina al tener n-1 aristas.

Complejidad: O(E log E) por el ordenamiento.
"""


class UnionFind:
    """Conjuntos disjuntos con compresión de caminos y unión por rango."""

    def __init__(self, n):
        self.padre = list(range(n))
        self.rango = [0] * n

    def encontrar(self, x):
        raiz = x
        while self.padre[raiz] != raiz:
            raiz = self.padre[raiz]
        while self.padre[x] != raiz:              # compresión de caminos
            self.padre[x], x = raiz, self.padre[x]
        return raiz

    def unir(self, a, b):
        ra, rb = self.encontrar(a), self.encontrar(b)
        if ra == rb:
            return False
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        return True


def kruskal(grafo):
    """Regresa (aristas_del_arbol, peso_total, pasos).

    `pasos` es una lista de (peso, u, v, aceptada) en el orden en que se
    evaluó cada arista; sirve para la animación paso a paso de la GUI.
    """
    conjuntos = UnionFind(grafo.num_nodos)
    arbol = []
    pasos = []
    total = 0
    for peso, u, v in sorted(grafo.aristas):
        aceptada = conjuntos.unir(u, v)
        pasos.append((peso, u, v, aceptada))
        if aceptada:
            arbol.append((peso, u, v))
            total += peso
            if len(arbol) == grafo.num_nodos - 1:
                break
    return arbol, total, pasos
