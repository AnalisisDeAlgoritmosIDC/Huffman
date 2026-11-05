import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mst import Grafo, generar_grafo_aleatorio, kruskal, prim, UnionFind


def fuerza_bruta(grafo):
    """Peso mínimo probando todos los subconjuntos de n-1 aristas (grafos chicos)."""
    mejor = None
    for combo in itertools.combinations(grafo.aristas, grafo.num_nodos - 1):
        uf = UnionFind(grafo.num_nodos)
        if all(uf.unir(u, v) for _, u, v in combo):
            peso = sum(p for p, _, _ in combo)
            mejor = peso if mejor is None else min(mejor, peso)
    return mejor


class PruebasMST(unittest.TestCase):
    def test_ejemplo_clasico(self):
        g = Grafo(5)
        for u, v, p in [(0, 1, 2), (0, 3, 6), (1, 2, 3), (1, 3, 8), (1, 4, 5), (2, 4, 7), (3, 4, 9)]:
            g.agregar_arista(u, v, p)
        self.assertEqual(kruskal(g)[1], 16)
        self.assertEqual(prim(g)[1], 16)

    def test_kruskal_y_prim_coinciden(self):
        for semilla in range(30):
            g = generar_grafo_aleatorio(12, densidad=0.5, semilla=semilla)
            self.assertTrue(g.es_conexo())
            ak, pk, _ = kruskal(g)
            ap, pp, _ = prim(g)
            self.assertEqual(len(ak), g.num_nodos - 1)
            self.assertEqual(len(ap), g.num_nodos - 1)
            self.assertEqual(pk, pp)

    def test_contra_fuerza_bruta(self):
        for semilla in range(5):
            g = generar_grafo_aleatorio(6, densidad=0.4, semilla=semilla)
            if len(g.aristas) > 14:
                continue
            self.assertEqual(kruskal(g)[1], fuerza_bruta(g))


if __name__ == "__main__":
    unittest.main()
