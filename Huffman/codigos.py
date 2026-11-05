"""
Generación de los códigos binarios de Huffman recorriendo el árbol.
Ir a la izquierda agrega un '0' y a la derecha un '1'.
"""


def generar_codigos(raiz):
    """Regresa un diccionario {caracter: codigo_binario_como_texto}."""
    codigos = {}
    if raiz is None:
        return codigos

    # Recorrido iterativo (evita límites de recursión en árboles muy profundos)
    pila = [(raiz, "")]
    while pila:
        nodo, prefijo = pila.pop()
        if nodo.es_hoja():
            codigos[nodo.caracter] = prefijo or "0"
            continue
        if nodo.derecha is not None:
            pila.append((nodo.derecha, prefijo + "1"))
        if nodo.izquierda is not None:
            pila.append((nodo.izquierda, prefijo + "0"))
    return codigos


def es_codigo_prefijo(codigos):
    """Verifica que ningún código sea prefijo de otro (propiedad de Huffman)."""
    lista = sorted(codigos.values())
    for i in range(len(lista) - 1):
        if lista[i + 1].startswith(lista[i]):
            return False
    return True
