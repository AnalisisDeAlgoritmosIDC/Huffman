"""
Grafo no dirigido y ponderado para los algoritmos de árbol de expansión mínima.
"""
import math
import random


class Grafo:
    def __init__(self, num_nodos=0):
        self.num_nodos = num_nodos
        self.aristas = []          # lista de (peso, u, v)
        self.posiciones = []       # (x, y) de cada nodo, solo para dibujar

    def agregar_arista(self, u, v, peso):
        self.aristas.append((peso, u, v))

    def adyacencia(self):
        """Lista de adyacencia: ady[u] = [(peso, v), ...]"""
        ady = [[] for _ in range(self.num_nodos)]
        for peso, u, v in self.aristas:
            ady[u].append((peso, v))
            ady[v].append((peso, u))
        return ady

    def es_conexo(self):
        if self.num_nodos == 0:
            return True
        ady = self.adyacencia()
        vistos = {0}
        pila = [0]
        while pila:
            u = pila.pop()
            for _, v in ady[u]:
                if v not in vistos:
                    vistos.add(v)
                    pila.append(v)
        return len(vistos) == self.num_nodos


def etiqueta(nodo):
    """0 -> 'A', 25 -> 'Z', 26 -> 'A1', ..."""
    letra = chr(ord("A") + nodo % 26)
    vuelta = nodo // 26
    return letra if vuelta == 0 else "%s%d" % (letra, vuelta)


def generar_grafo_aleatorio(num_nodos, densidad=0.3, semilla=None, ancho=700, alto=480, margen=40):
    """Genera un grafo conexo con posiciones en el plano.

    El peso de cada arista es la distancia euclidiana entre los nodos
    (dividida entre 10), así el dibujo es coherente con los pesos.
    `densidad` (0-1) controla cuántas aristas extra se agregan además
    de las necesarias para que el grafo sea conexo.
    """
    rnd = random.Random(semilla)
    grafo = Grafo(num_nodos)

    # 1) Posiciones con separación mínima entre nodos
    separacion = max(35, min(ancho, alto) / (math.sqrt(num_nodos) + 1) * 0.6)
    intentos = 0
    while len(grafo.posiciones) < num_nodos:
        x = rnd.uniform(margen, ancho - margen)
        y = rnd.uniform(margen, alto - margen)
        intentos += 1
        if intentos > 5000 or all(math.dist((x, y), p) >= separacion for p in grafo.posiciones):
            grafo.posiciones.append((x, y))

    def peso(u, v):
        return max(1, round(math.dist(grafo.posiciones[u], grafo.posiciones[v]) / 10))

    existentes = set()

    def agregar(u, v):
        clave = (min(u, v), max(u, v))
        if u != v and clave not in existentes:
            existentes.add(clave)
            grafo.agregar_arista(u, v, peso(u, v))

    # 2) Garantizar conexidad: cada nodo se une al más cercano de los ya conectados
    orden = list(range(num_nodos))
    rnd.shuffle(orden)
    for i in range(1, num_nodos):
        actual = orden[i]
        cercano = min(orden[:i], key=lambda o: math.dist(grafo.posiciones[actual], grafo.posiciones[o]))
        agregar(actual, cercano)

    # 3) Aristas extra entre vecinos cercanos según la densidad
    extra_por_nodo = max(1, round(densidad * 6))
    for u in range(num_nodos):
        vecinos = sorted(
            (v for v in range(num_nodos) if v != u),
            key=lambda v: math.dist(grafo.posiciones[u], grafo.posiciones[v]),
        )
        for v in vecinos[: extra_por_nodo + 1]:
            if rnd.random() < 0.5 + densidad / 2:
                agregar(u, v)

    return grafo
