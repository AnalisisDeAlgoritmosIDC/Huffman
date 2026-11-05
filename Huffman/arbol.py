"""
Construcción del árbol de Huffman usando la técnica voraz (greedy).

Idea voraz: en cada paso se toman los DOS nodos con menor frecuencia,
se unen en un nodo padre cuya frecuencia es la suma de ambos y el padre
se regresa a la cola de prioridad. Se repite hasta que queda un solo nodo
(la raíz). La elección local "unir los dos menos frecuentes" produce un
código prefijo óptimo global.

Complejidad: O(n log n) con n = número de caracteres distintos,
porque se hacen n-1 uniones y cada operación del heap cuesta O(log n).
"""
import heapq
import itertools


class Nodo:
    """Nodo del árbol de Huffman. Las hojas guardan un carácter."""

    __slots__ = ("frecuencia", "caracter", "izquierda", "derecha")

    def __init__(self, frecuencia, caracter=None, izquierda=None, derecha=None):
        self.frecuencia = frecuencia
        self.caracter = caracter
        self.izquierda = izquierda
        self.derecha = derecha

    def es_hoja(self):
        return self.izquierda is None and self.derecha is None

    def __repr__(self):
        if self.es_hoja():
            return "Hoja(%r, %d)" % (self.caracter, self.frecuencia)
        return "Nodo(%d)" % self.frecuencia


def construir_arbol(frecuencias):
    """Construye el árbol de Huffman.

    Regresa (raiz, pasos) donde `pasos` es la lista de uniones voraces
    realizadas: cada elemento es (nodo_izquierdo, nodo_derecho, nodo_padre).

    El orden inicial es determinista (frecuencia y luego carácter) para que
    al descomprimir se reconstruya exactamente el mismo árbol a partir de la
    tabla de frecuencias guardada en el archivo .huf.
    """
    pasos = []
    if not frecuencias:
        return None, pasos

    # El contador desempata nodos con la misma frecuencia (los nodos no se comparan)
    contador = itertools.count()
    heap = []
    for caracter, frecuencia in sorted(frecuencias.items(), key=lambda p: (p[1], p[0])):
        heap.append((frecuencia, next(contador), Nodo(frecuencia, caracter)))
    heapq.heapify(heap)

    # Caso especial: un solo carácter distinto -> se le asigna el código "0"
    if len(heap) == 1:
        frecuencia, _, hoja = heap[0]
        return Nodo(frecuencia, izquierda=hoja), pasos

    while len(heap) > 1:
        frec_a, _, menor = heapq.heappop(heap)          # elección voraz 1
        frec_b, _, segundo_menor = heapq.heappop(heap)  # elección voraz 2
        padre = Nodo(frec_a + frec_b, izquierda=menor, derecha=segundo_menor)
        pasos.append((menor, segundo_menor, padre))
        heapq.heappush(heap, (padre.frecuencia, next(contador), padre))

    return heap[0][2], pasos


def altura(raiz):
    """Altura del árbol (número de aristas del camino más largo)."""
    if raiz is None:
        return 0
    maximo = 0
    pila = [(raiz, 0)]
    while pila:
        nodo, nivel = pila.pop()
        maximo = max(maximo, nivel)
        if nodo.izquierda:
            pila.append((nodo.izquierda, nivel + 1))
        if nodo.derecha:
            pila.append((nodo.derecha, nivel + 1))
    return maximo


def contar_nodos(raiz):
    """Total de nodos (hojas + internos)."""
    if raiz is None:
        return 0
    total = 0
    pila = [raiz]
    while pila:
        nodo = pila.pop()
        total += 1
        if nodo.izquierda:
            pila.append(nodo.izquierda)
        if nodo.derecha:
            pila.append(nodo.derecha)
    return total
