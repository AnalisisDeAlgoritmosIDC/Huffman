"""
Puente entre la página web (JavaScript) y el código de Python del proyecto.

En el navegador este archivo corre dentro de Pyodide (Python compilado a
WebAssembly), así que la página usa EXACTAMENTE los mismos módulos
huffman/, mst/ e idioma/ que se prueban con unittest en la carpeta tests/.

Cada función regresa un texto JSON que JavaScript convierte con JSON.parse.
"""
import datetime
import json
import math
import os
import time
from itertools import accumulate

from huffman import (
    leer_texto, calcular_frecuencias, ordenar_frecuencias, describir_caracter,
    construir_arbol, altura, contar_nodos, generar_codigos, codificar,
    guardar_comprimido, descomprimir_y_verificar, leer_mc, longitud_promedio, entropia,
)
from mst import generar_grafo_aleatorio, kruskal, prim, etiqueta
from idioma import detectar_idioma

CARPETA = "/tmp/huffman_web"
RUTA_TXT = CARPETA + "/original.txt"
RUTA_HUF = CARPETA + "/comprimido.mc"
RUTA_DEC = CARPETA + "/decodificado.txt"
RUTA_INSP = CARPETA + "/inspeccion.mc"          # archivo que examina el Inspector
RUTA_INSP_DEC = CARPETA + "/inspeccion_recuperado.txt"
os.makedirs(CARPETA, exist_ok=True)

ESTADO = {}


def _arbol_a_dict(raiz):
    """Convierte el árbol a diccionarios anidados para dibujarlo en JS.
    f = frecuencia, c = carácter (solo hojas), i/d = hijo izquierdo/derecho."""
    if raiz is None:
        return None
    nodo = {"f": raiz.frecuencia}
    if raiz.es_hoja():
        nodo["c"] = describir_caracter(raiz.caracter)
        return nodo
    if raiz.izquierda is not None:
        nodo["i"] = _arbol_a_dict(raiz.izquierda)
    if raiz.derecha is not None:
        nodo["d"] = _arbol_a_dict(raiz.derecha)
    return nodo


def _nombre(nodo):
    if nodo.es_hoja():
        return "'%s' (%d)" % (describir_caracter(nodo.caracter), nodo.frecuencia)
    return "nodo interno (%d)" % nodo.frecuencia


def _construccion(frecuencias, pasos):
    """Numera los nodos para poder animar la cola de prioridad en JS.
    Regresa (nodos, fusiones): nodos[i] = {f, c}; fusiones = [[a, b, nuevo], ...]."""
    nodos, ids = [], {}

    def nid(nodo):
        if id(nodo) not in ids:
            ids[id(nodo)] = len(nodos)
            nodos.append({"f": nodo.frecuencia,
                          "c": describir_caracter(nodo.caracter) if nodo.es_hoja() else None})
        return ids[id(nodo)]

    # Primero las hojas, en el mismo orden en que entran al heap
    hojas = {}
    for a, b, _ in pasos:
        for n in (a, b):
            if n.es_hoja():
                hojas[n.caracter] = n
    for car, _ in sorted(frecuencias.items(), key=lambda p: (p[1], p[0])):
        if car in hojas:
            nid(hojas[car])
    fusiones = [[nid(a), nid(b), nid(p)] for a, b, p in pasos]
    return nodos, fusiones


def _curva_ahorro(texto, codigos, puntos=300):
    """Bits acumulados (original en UTF-8 vs Huffman) a lo largo del texto."""
    n = len(texto)
    if n == 0:
        return []
    largo_huf = {c: len(cod) for c, cod in codigos.items()}
    largo_ori = {c: len(c.encode("utf-8")) * 8 for c in codigos}
    paso = max(1, n // puntos)
    huf = list(accumulate(map(largo_huf.__getitem__, texto)))
    ori = list(accumulate(map(largo_ori.__getitem__, texto)))
    indices = list(range(paso - 1, n, paso))
    if indices[-1] != n - 1:
        indices.append(n - 1)
    return [[i + 1, ori[i], huf[i]] for i in indices]


def analizar():
    """Lee RUTA_TXT, cuenta frecuencias, construye el árbol y los códigos."""
    t0 = time.perf_counter()
    texto, codificacion = leer_texto(RUTA_TXT)
    frecuencias = calcular_frecuencias(texto)
    raiz, pasos = construir_arbol(frecuencias)
    codigos = generar_codigos(raiz)
    t1 = time.perf_counter()
    ESTADO.clear()
    ESTADO.update(texto=texto, codificacion=codificacion, frecuencias=frecuencias,
                  raiz=raiz, codigos=codigos)

    total = len(texto) or 1
    tabla = []
    for car, frec in ordenar_frecuencias(frecuencias):
        tabla.append({"car": describir_caracter(car), "frec": frec, "prob": frec / total,
                      "codigo": codigos[car]})
    original = os.path.getsize(RUTA_TXT)
    l = longitud_promedio(frecuencias, codigos)
    h = entropia(frecuencias)
    nodos, fusiones = _construccion(frecuencias, pasos)
    t2 = time.perf_counter()
    idioma = detectar_idioma(texto)
    t3 = time.perf_counter()
    return json.dumps({
        "caracteres": len(texto),
        "distintos": len(frecuencias),
        "codificacion": codificacion,
        "original": original,
        "tabla": tabla,
        "arbol": _arbol_a_dict(raiz),
        "pasos": [[_nombre(a), _nombre(b), p.frecuencia] for a, b, p in pasos],
        "prom": l,
        "fijo": original * 8 / total,
        "entropia": h,
        "eficiencia": h / l * 100 if l else 0,
        "hojas": len(frecuencias),
        "nodos": contar_nodos(raiz),
        "altura": altura(raiz),
        "t_analisis": t1 - t0,
        "t_idioma": t3 - t2,
        "muestra": texto[:6000],
        "codigos_crudos": codigos,
        "nodos": nodos,
        "fusiones": fusiones,
        "curva": _curva_ahorro(texto, codigos),
        "idioma": idioma,
    }, ensure_ascii=False)


def comprimir(nombre_original=""):
    """Codifica el texto y escribe RUTA_HUF (formato .mc versión 2)."""
    t0 = time.perf_counter()
    bits = codificar(ESTADO["texto"], ESTADO["codigos"])
    with open(RUTA_TXT, "rb") as archivo:
        datos_originales = archivo.read()
    tam_huf = guardar_comprimido(RUTA_HUF, ESTADO["frecuencias"], bits, ESTADO["codificacion"],
                                 datos_originales, nombre_original)
    t1 = time.perf_counter()
    original = len(datos_originales)
    return json.dumps({
        "bits": len(bits),
        "datos": math.ceil(len(bits) / 8),
        "huf": tam_huf,
        "ahorro": (1 - tam_huf / original) * 100 if original else 0,
        "razon": original / tam_huf if tam_huf else 0,
        "ahorrados": original - tam_huf,
        "t_cod": t1 - t0,
        "muestra_bits": bits[:4000],
    })


def descomprimir():
    """Lee RUTA_HUF, reconstruye el árbol, escribe RUTA_DEC y compara con el original."""
    t0 = time.perf_counter()
    texto, verificacion = descomprimir_y_verificar(RUTA_HUF, RUTA_DEC)
    t1 = time.perf_counter()
    identico = None
    if os.path.exists(RUTA_TXT):
        with open(RUTA_TXT, "rb") as a, open(RUTA_DEC, "rb") as b:
            identico = a.read() == b.read()
    return json.dumps({
        "t_dec": t1 - t0,
        "identico": identico,
        "caracteres": len(texto),
        "tamano": os.path.getsize(RUTA_DEC),
        "sha256_ok": verificacion["sha256_ok"],
        "muestra": texto[:6000],
    })


def inspeccionar():
    """Examina el archivo .mc en RUTA_INSP SIN descomprimirlo: encabezado,
    tabla de frecuencias, códigos y árbol reconstruidos, secciones y bytes."""
    with open(RUTA_INSP, "rb") as archivo:
        crudo = archivo.read()
    info = leer_mc(crudo)
    frecuencias = info["frecuencias"]
    raiz, _ = construir_arbol(frecuencias)
    codigos = generar_codigos(raiz)
    total = sum(frecuencias.values()) or 1
    original = info["tamano_original"]
    comprimido = info["tamano_comprimido"]
    inicio = info["inicio_datos"]
    return json.dumps({
        "version": info["version"],
        "tamano_original": original,
        "tamano_comprimido": comprimido,
        "ahorrados": None if original is None else original - comprimido,
        "ahorro": None if not original else (1 - comprimido / original) * 100,
        "razon": None if not original else original / comprimido,
        "caracteres": info["caracteres"],
        "simbolos": info["simbolos"],
        "bits_validos": info["bits_validos"],
        "relleno": info["relleno"],
        "bytes_datos": comprimido - inicio,
        "fecha": None if info["fecha"] is None else
                 datetime.datetime.fromtimestamp(info["fecha"], datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "sha256": info["sha256"],
        "nombre_original": info["nombre_original"],
        "codificacion": info["codificacion"],
        "secciones": info["secciones"],
        "inicio_hex": crudo[:min(inicio, 384)].hex(),
        "inicio_datos": inicio,
        "datos_hex": crudo[inicio:inicio + 96].hex(),
        "muestra_bits": info["bits"][:768],
        "tabla": [{"car": describir_caracter(c), "frec": f, "prob": f / total, "codigo": codigos[c]}
                  for c, f in ordenar_frecuencias(frecuencias)],
        "arbol": _arbol_a_dict(raiz),
        "prom": longitud_promedio(frecuencias, codigos),
        "entropia": entropia(frecuencias),
    }, ensure_ascii=False)


def descomprimir_inspector():
    """Descomprime el .mc del Inspector y verifica su integridad con el SHA-256 guardado."""
    t0 = time.perf_counter()
    texto, verificacion = descomprimir_y_verificar(RUTA_INSP, RUTA_INSP_DEC)
    t1 = time.perf_counter()
    verificacion.update({"t_dec": t1 - t0, "caracteres": len(texto), "muestra": texto[:8000]})
    return json.dumps(verificacion, ensure_ascii=False)


def grafo(nodos, densidad, semilla, algoritmo, inicio):
    """Genera el grafo y corre Kruskal o Prim. Regresa todo lo necesario para animarlo."""
    g = generar_grafo_aleatorio(int(nodos), float(densidad), semilla)
    t0 = time.perf_counter()
    if algoritmo == "Kruskal":
        arbol, total, pasos = kruskal(g)
        otro = prim(g)[1]
    else:
        arbol, total, pasos = prim(g, int(inicio))
        otro = kruskal(g)[1]
    t1 = time.perf_counter()
    return json.dumps({
        "etiquetas": [etiqueta(i) for i in range(g.num_nodos)],
        "posiciones": g.posiciones,
        "aristas": [[u, v, p] for p, u, v in g.aristas],
        "pasos": [[u, v, p, ok] for p, u, v, ok in pasos],
        "total": total,
        "otro_total": otro,
        "aristas_arbol": len(arbol),
        "tiempo": t1 - t0,
    })
