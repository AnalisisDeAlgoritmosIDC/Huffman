"""
Codificación y decodificación del texto con los códigos de Huffman,
y lectura/escritura del archivo comprimido (.mc).

Formato del archivo .mc, versión 2 (todos los enteros en big-endian):

    ENCABEZADO
    offset  bytes  campo
         0      3  firma b"HMC" (Huffmanificador Comprimido)
         3      1  versión del formato (2)
         4      8  tamaño del archivo original en bytes
        12      8  número de caracteres del texto original
        20      8  total de bits codificados válidos
        28      1  bits de relleno agregados al último byte (0-7)
        29      8  fecha de creación (segundos desde 1970, UTC)
        37     32  SHA-256 del archivo original (para verificar la integridad)
        69      1  largo L1 del nombre de la codificación del texto
        70     L1  codificación (ej. "utf-8")
         .      2  largo L2 del nombre del archivo original (UTF-8)
         .     L2  nombre del archivo original
    TABLA DE FRECUENCIAS (para reconstruir el árbol)
         .      4  número de símbolos distintos K
                   K veces: 1 byte largo del símbolo en UTF-8 + bytes del símbolo
                            + 4 bytes con su frecuencia
    DATOS
         .      ⌈bits / 8⌉  bits codificados empaquetados en bytes

También se pueden leer archivos de la versión 1 (firma b"HMC1"), que no
guardaban tamaño original, hash, fecha ni nombre.
"""
import hashlib
import struct
import time

from .arbol import construir_arbol

FIRMA = b"HMC"
VERSION = 2
FIRMA_V1 = b"HMC1"
HASH_VACIO = bytes(32)


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


def guardar_comprimido(ruta, frecuencias, bits, codificacion="utf-8", datos_originales=None, nombre_original=""):
    """Escribe el archivo .mc (versión 2). Regresa el tamaño total en bytes.

    `datos_originales` son los bytes del .txt original: de ahí salen el tamaño
    original y el SHA-256. Si no se dan, el tamaño se calcula con las
    frecuencias y el hash queda en ceros (no disponible).
    """
    datos, relleno = bits_a_bytes(bits)
    if datos_originales is not None:
        tamano = len(datos_originales)
        huella = hashlib.sha256(datos_originales).digest()
    else:
        tamano = sum(len(c.encode(codificacion)) * f for c, f in frecuencias.items())
        huella = HASH_VACIO
    caracteres = sum(frecuencias.values())
    cod = codificacion.encode("ascii")
    nombre = nombre_original.encode("utf-8")[:65535]

    with open(ruta, "wb") as archivo:
        archivo.write(FIRMA + bytes([VERSION]))
        archivo.write(struct.pack(">QQQB", tamano, caracteres, len(bits), relleno))
        archivo.write(struct.pack(">Q", int(time.time())))
        archivo.write(huella)
        archivo.write(struct.pack(">B", len(cod)) + cod)
        archivo.write(struct.pack(">H", len(nombre)) + nombre)
        archivo.write(struct.pack(">I", len(frecuencias)))
        for caracter, frecuencia in frecuencias.items():
            c = caracter.encode("utf-8")
            archivo.write(struct.pack(">B", len(c)) + c + struct.pack(">I", frecuencia))
        archivo.write(datos)
        return archivo.tell()


def leer_mc(contenido):
    """Interpreta un .mc (bytes o ruta) SIN descomprimirlo.

    Regresa un diccionario con todos los campos del encabezado, la tabla de
    frecuencias, los bits codificados y las secciones del archivo
    (nombre, offset, tamaño) para poder inspeccionarlo.
    """
    if isinstance(contenido, str):
        with open(contenido, "rb") as archivo:
            contenido = archivo.read()

    secciones = []
    if contenido[:4] == FIRMA_V1:
        version, pos = 1, 4
        secciones.append(("Firma y versión", 0, 4))
        info = {"tamano_original": None, "caracteres": None, "bits_validos": None,
                "fecha": None, "sha256": None, "nombre_original": ""}
        inicio = pos
        (largo_cod,) = struct.unpack_from(">B", contenido, pos)
        codificacion = contenido[pos + 1: pos + 1 + largo_cod].decode("ascii")
        pos += 1 + largo_cod
        secciones.append(("Codificación", inicio, pos - inicio))
    elif contenido[:3] == FIRMA and len(contenido) >= 72:
        version = contenido[3]
        if version != VERSION:
            raise ValueError("Versión de formato .mc no soportada: %d" % version)
        secciones.append(("Firma y versión", 0, 4))
        tamano, caracteres, bits_validos, relleno = struct.unpack_from(">QQQB", contenido, 4)
        (fecha,) = struct.unpack_from(">Q", contenido, 29)
        huella = contenido[37:69]
        secciones.append(("Tamaños, bits y relleno", 4, 25))
        secciones.append(("Fecha", 29, 8))
        secciones.append(("SHA-256 del original", 37, 32))
        pos = 69
        inicio = pos
        (largo_cod,) = struct.unpack_from(">B", contenido, pos)
        codificacion = contenido[pos + 1: pos + 1 + largo_cod].decode("ascii")
        pos += 1 + largo_cod
        (largo_nombre,) = struct.unpack_from(">H", contenido, pos)
        nombre = contenido[pos + 2: pos + 2 + largo_nombre].decode("utf-8", errors="replace")
        pos += 2 + largo_nombre
        secciones.append(("Codificación y nombre", inicio, pos - inicio))
        info = {"tamano_original": tamano, "caracteres": caracteres, "bits_validos": bits_validos,
                "fecha": fecha, "sha256": None if huella == HASH_VACIO else huella.hex(),
                "nombre_original": nombre}
    else:
        raise ValueError("El archivo no es un .mc válido (firma incorrecta)")

    inicio = pos
    (k,) = struct.unpack_from(">I", contenido, pos)
    pos += 4
    frecuencias = {}
    for _ in range(k):
        (largo,) = struct.unpack_from(">B", contenido, pos)
        caracter = contenido[pos + 1: pos + 1 + largo].decode("utf-8")
        pos += 1 + largo
        (frecuencia,) = struct.unpack_from(">I", contenido, pos)
        pos += 4
        frecuencias[caracter] = frecuencia
    secciones.append(("Tabla de frecuencias", inicio, pos - inicio))

    if version == 1:
        (relleno,) = struct.unpack_from(">B", contenido, pos)
        secciones.append(("Relleno", pos, 1))
        pos += 1

    datos = contenido[pos:]
    secciones.append(("Datos comprimidos", pos, len(datos)))
    bits = bytes_a_bits(datos, relleno)
    if version == 1:
        info["bits_validos"] = len(bits)
        info["caracteres"] = sum(frecuencias.values())

    info.update({
        "version": version,
        "codificacion": codificacion,
        "relleno": relleno,
        "simbolos": len(frecuencias),
        "frecuencias": frecuencias,
        "bits": bits,
        "tamano_comprimido": len(contenido),
        "inicio_datos": pos,
        "secciones": secciones,
    })
    return info


def leer_comprimido(ruta):
    """Lee un .mc. Regresa (frecuencias, bits, codificacion)."""
    info = leer_mc(ruta)
    return info["frecuencias"], info["bits"], info["codificacion"]


def descomprimir_y_verificar(ruta_mc, ruta_salida=None):
    """Descomprime un .mc y verifica su integridad con lo guardado en el encabezado.

    Regresa (texto, verificacion) donde verificacion indica si coinciden el
    tamaño y el SHA-256 del resultado con los del archivo original.
    """
    info = leer_mc(ruta_mc)
    raiz, _ = construir_arbol(info["frecuencias"])
    texto = decodificar(info["bits"], raiz)
    datos = texto.encode(info["codificacion"])
    if ruta_salida:
        with open(ruta_salida, "wb") as archivo:
            archivo.write(datos)
    huella = hashlib.sha256(datos).hexdigest()
    verificacion = {
        "tamano": len(datos),
        "tamano_ok": None if info["tamano_original"] is None else len(datos) == info["tamano_original"],
        "sha256": huella,
        "sha256_ok": None if info["sha256"] is None else huella == info["sha256"],
    }
    return texto, verificacion


def descomprimir_archivo(ruta_mc, ruta_salida=None):
    """Lee un .mc, reconstruye el árbol y regresa el texto original.
    Si se da `ruta_salida`, también lo guarda en disco."""
    return descomprimir_y_verificar(ruta_mc, ruta_salida)[0]
