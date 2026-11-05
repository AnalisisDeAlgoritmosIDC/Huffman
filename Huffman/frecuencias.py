"""
Lectura del archivo de texto y cálculo de frecuencias de cada carácter.
"""
from collections import Counter

# Codificaciones que se intentan, en orden, al leer el archivo
# (si el archivo trae BOM, se conserva como un carácter más para que la
# descompresión regrese exactamente los mismos bytes)
CODIFICACIONES = ("utf-8", "latin-1")


def leer_texto(ruta):
    """Lee un archivo .txt y regresa (texto, codificacion_usada).

    Se lee en modo binario para que los saltos de línea (\\r\\n o \\n)
    se conserven exactamente igual y la decodificación sea idéntica al original.
    """
    with open(ruta, "rb") as archivo:
        datos = archivo.read()

    for codificacion in CODIFICACIONES:
        try:
            return datos.decode(codificacion), codificacion
        except UnicodeDecodeError:
            continue
    # latin-1 nunca falla, pero por si acaso:
    return datos.decode("latin-1", errors="replace"), "latin-1"


def calcular_frecuencias(texto):
    """Regresa un diccionario {caracter: numero_de_apariciones}."""
    return dict(Counter(texto))


def ordenar_frecuencias(frecuencias):
    """Lista de (caracter, frecuencia) de mayor a menor frecuencia."""
    return sorted(frecuencias.items(), key=lambda par: (-par[1], par[0]))


NOMBRES_ESPECIALES = {
    " ": "␣ (espacio)",
    "\n": "\\n (salto)",
    "\r": "\\r (retorno)",
    "\t": "\\t (tab)",
    "﻿": "BOM",
}


def describir_caracter(caracter):
    """Texto legible para mostrar un carácter en la tabla o en el árbol."""
    if caracter in NOMBRES_ESPECIALES:
        return NOMBRES_ESPECIALES[caracter]
    if not caracter.isprintable():
        return "U+%04X" % ord(caracter)
    return caracter
