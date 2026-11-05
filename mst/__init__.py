"""Paquete con los algoritmos de árbol de expansión mínima (Kruskal y Prim)."""
from .grafo import Grafo, generar_grafo_aleatorio, etiqueta
from .kruskal import kruskal, UnionFind
from .prim import prim
