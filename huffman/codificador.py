"""
Codificación y decodificación del texto con los códigos de Huffman,
y lectura/escritura del archivo comprimido (.mc).

Formato del archivo .mc:
    4 bytes   firma b"HMC1"
    1 byte    largo del nombre de la codificación del texto (ej. "utf-8")
    n bytes   nombre de la codificación
    4 bytes   número de caracteres distintos (K)
    K veces:  1 byte largo del carácter en UTF-8 + bytes del carácter
              + 4 bytes con su frecuencia
    1 byte    bits de relleno agregados al final (0-7)
    resto     los bits codificados empaquetados en bytes
"""
import struct

from .arbol import construir_arbol

FIRMA = b"HMC1"


def codificar(texto, codigos):
    """Convierte el texto en una cadena de '0' y '1'."""
    return "".join(map(codigos.__getitem__, texto))


def decodificar(bits, raiz):
    """Recorre el árbol bit por bit; al llegar a una hoja emite su carácter."""
    if raiz is None:
        return ""
    resultado = []
    agregar = resultado.append
    nodo = raiz
    for bit in bits:
        nodo = nodo.izquierda if bit == "0" else nodo.derecha
        if nodo.izquierda is None and nodo.derecha is None:
            agregar(nodo.caracter)
            nodo = raiz
    return "".join(resultado)


def bits_a_bytes(bits):
    """Empaqueta la cadena de bits en bytes. Regresa (bytes, relleno)."""
    relleno = (8 - len(bits) % 8) % 8
    bits = bits + "0" * relleno
    if not bits:
        return b"", 0
    return int(bits, 2).to_bytes(len(bits) // 8, "big"), relleno


def bytes_a_bits(datos, relleno):
    """Operación inversa de bits_a_bytes."""
    if not datos:
        return ""
    bits = bin(int.from_bytes(datos, "big"))[2:].zfill(len(datos) * 8)
    return bits[: len(bits) - relleno] if relleno else bits


def guardar_comprimido(ruta, frecuencias, bits, codificacion="utf-8"):
    """Escribe el archivo .mc. Regresa el tamaño total en bytes."""
    datos, relleno = bits_a_bytes(bits)
    nombre_cod = codificacion.encode("ascii")
    with open(ruta, "wb") as archivo:
        archivo.write(FIRMA)
        archivo.write(struct.pack(">B", len(nombre_cod)))
        archivo.write(nombre_cod)
        archivo.write(struct.pack(">I", len(frecuencias)))
        for caracter, frecuencia in frecuencias.items():
            c = caracter.encode("utf-8")
            archivo.write(struct.pack(">B", len(c)))
            archivo.write(c)
            archivo.write(struct.pack(">I", frecuencia))
        archivo.write(struct.pack(">B", relleno))
        archivo.write(datos)
        return archivo.tell()


def leer_comprimido(ruta):
    """Lee un .mc. Regresa (frecuencias, bits, codificacion)."""
    with open(ruta, "rb") as archivo:
        contenido = archivo.read()

    if contenido[:4] != FIRMA:
        raise ValueError("El archivo no es un .mc válido (firma incorrecta)")
    pos = 4
    (largo_cod,) = struct.unpack_from(">B", contenido, pos)
    pos += 1
    codificacion = contenido[pos : pos + largo_cod].decode("ascii")
    pos += largo_cod
    (k,) = struct.unpack_from(">I", contenido, pos)
    pos += 4
    frecuencias = {}
    for _ in range(k):
        (largo,) = struct.unpack_from(">B", contenido, pos)
        pos += 1
        caracter = contenido[pos : pos + largo].decode("utf-8")
        pos += largo
        (frecuencia,) = struct.unpack_from(">I", contenido, pos)
        pos += 4
        frecuencias[caracter] = frecuencia
    (relleno,) = struct.unpack_from(">B", contenido, pos)
    pos += 1
    bits = bytes_a_bits(contenido[pos:], relleno)
    return frecuencias, bits, codificacion


def descomprimir_archivo(ruta_huf, ruta_salida=None):
    """Lee un .mc, reconstruye el árbol y regresa el texto original.
    Si se da `ruta_salida`, también lo guarda en disco."""
    frecuencias, bits, codificacion = leer_comprimido(ruta_huf)
    raiz, _ = construir_arbol(frecuencias)
    texto = decodificar(bits, raiz)
    if ruta_salida:
        with open(ruta_salida, "wb") as archivo:
            archivo.write(texto.encode(codificacion))
    return texto
