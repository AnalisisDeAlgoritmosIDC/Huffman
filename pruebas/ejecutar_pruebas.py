"""
Ejecuta las pruebas mínimas que pide la actividad y deja la evidencia en
pruebas/RESULTADOS.md y en pruebas/salidas/ (los .mc y los .txt recuperados).

    python pruebas/ejecutar_pruebas.py

1. Texto pequeño: frecuencias y códigos comprobables a mano.
2. Libro de Project Gutenberg: archivo real de mayor tamaño.
3. Integridad: comprimir -> descomprimir -> comparar byte a byte y SHA-256,
   y detectar un archivo .mc alterado.
4. Archivo no utilizado durante el desarrollo.
"""
import hashlib
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from huffman import (leer_texto, calcular_frecuencias, ordenar_frecuencias, describir_caracter,
                     construir_arbol, generar_codigos, codificar, guardar_comprimido, leer_mc,
                     descomprimir_y_verificar, longitud_promedio, entropia)

AQUI = os.path.join(RAIZ, "pruebas")
SALIDAS = os.path.join(AQUI, "salidas")

CASOS = [
    ("1. Texto pequeño", os.path.join(AQUI, "1_texto_pequeno.txt")),
    ("2. Libro de Project Gutenberg (Alice, #11)", os.path.join(RAIZ, "libros", "alice_in_wonderland.txt")),
    ("4. Archivo no usado en el desarrollo (Persuasion, J. Austen)", os.path.join(AQUI, "4_archivo_nuevo_persuasion.txt")),
]


def kb(n):
    return "%.2f KB" % (n / 1024) if n < 1024 * 1024 else "%.2f MB" % (n / 1024 / 1024)


def comprimir_y_recuperar(ruta):
    """original.txt -> archivo.mc -> recuperado.txt, con mediciones."""
    nombre = os.path.basename(ruta)
    base = os.path.splitext(nombre)[0]
    ruta_mc = os.path.join(SALIDAS, base + ".mc")
    ruta_rec = os.path.join(SALIDAS, base + "_recuperado.txt")
    with open(ruta, "rb") as f:
        original = f.read()

    t0 = time.perf_counter()
    texto, cod = leer_texto(ruta)
    frec = calcular_frecuencias(texto)
    raiz, _ = construir_arbol(frec)
    codigos = generar_codigos(raiz)
    bits = codificar(texto, codigos)
    tam_mc = guardar_comprimido(ruta_mc, frec, bits, cod, original, nombre)
    t1 = time.perf_counter()
    _, verif = descomprimir_y_verificar(ruta_mc, ruta_rec)
    t2 = time.perf_counter()
    with open(ruta_rec, "rb") as f:
        recuperado = f.read()

    return {
        "nombre": nombre, "mc": os.path.basename(ruta_mc), "original": len(original), "comprimido": tam_mc,
        "ahorro": len(original) - tam_mc, "pct": (1 - tam_mc / len(original)) * 100 if original else 0,
        "simbolos": len(frec), "bits": len(bits), "prom": longitud_promedio(frec, codigos), "h": entropia(frec),
        "sha_original": hashlib.sha256(original).hexdigest(), "sha_recuperado": hashlib.sha256(recuperado).hexdigest(),
        "byte_a_byte": original == recuperado, "sha_ok": verif["sha256_ok"], "t_comp": t1 - t0, "t_desc": t2 - t1,
        "frec": frec, "codigos": codigos, "ruta_mc": ruta_mc,
    }


def prueba_corrupcion(ruta_mc):
    """Altera un bit de los datos de una copia del .mc y verifica que se detecte."""
    with open(ruta_mc, "rb") as f:
        crudo = bytearray(f.read())
    inicio = leer_mc(bytes(crudo))["inicio_datos"]
    crudo[inicio + (len(crudo) - inicio) // 2] ^= 0b00000100
    ruta_mala = os.path.join(SALIDAS, "alterado.mc")
    with open(ruta_mala, "wb") as f:
        f.write(crudo)
    _, verif = descomprimir_y_verificar(ruta_mala)
    os.remove(ruta_mala)
    return verif


def main():
    os.makedirs(SALIDAS, exist_ok=True)
    resultados = [(titulo, comprimir_y_recuperar(ruta)) for titulo, ruta in CASOS]
    pequeno = resultados[0][1]
    corrupcion = prueba_corrupcion(resultados[1][1]["ruta_mc"])

    md = ["# Resultados de las pruebas (generado por `pruebas/ejecutar_pruebas.py`)", "",
          "Flujo de cada prueba: `original.txt → archivo.mc → recuperado.txt`. Los archivos generados están en",
          "`pruebas/salidas/`.", "",
          "## Resumen", "",
          "| Prueba | Archivo | Original | Comprimido (.mc) | Ahorrado | Reducción | Símbolos | Byte a byte | SHA-256 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for titulo, r in resultados:
        md.append("| %s | `%s` | %s B (%s) | %s B (%s) | %s B | %.2f %% | %d | %s | %s |" % (
            titulo, r["nombre"], format(r["original"], ","), kb(r["original"]), format(r["comprimido"], ","),
            kb(r["comprimido"]), format(r["ahorro"], ","), r["pct"], r["simbolos"],
            "✔ idéntico" if r["byte_a_byte"] else "✘", "✔" if r["sha_ok"] else "✘"))

    md += ["", "## 1. Texto pequeño: «%s»" % open(CASOS[0][1], encoding="utf-8").read(), "",
           "Frecuencias y códigos que genera el programa (se comprueban a mano en `PRUEBAS.md`):", "",
           "| Símbolo | Frecuencia | Código | Bits × frecuencia |", "|---|---|---|---|"]
    for c, f in ordenar_frecuencias(pequeno["frec"]):
        cod = pequeno["codigos"][c]
        md.append("| `%s` | %d | `%s` | %d × %d = %d |" % (describir_caracter(c), f, cod, len(cod), f, len(cod) * f))
    md += ["", "Total: **%d bits** de datos codificados (vs. %d bits sin comprimir). El .mc pesa %d bytes porque su "
           "encabezado y tabla ocupan más que el texto: con textos tan pequeños el archivo comprimido es **más grande** "
           "que el original (ver «Limitaciones» en el README)." % (pequeno["bits"], pequeno["original"] * 8, pequeno["comprimido"]), ""]

    md += ["## 3. Integridad", "",
           "| Archivo | SHA-256 del original | SHA-256 del recuperado | Igual |", "|---|---|---|---|"]
    for _, r in resultados:
        md.append("| `%s` | `%s…` | `%s…` | %s |" % (r["nombre"], r["sha_original"][:24], r["sha_recuperado"][:24],
                                                    "✔" if r["sha_original"] == r["sha_recuperado"] else "✘"))
    md += ["", "**Archivo alterado:** se cambió 1 bit en los datos de `alice_in_wonderland.mc`. Al descomprimirlo, el "
           "SHA-256 del resultado %s el guardado en el encabezado → la página marca el archivo como dañado." %
           ("NO coincide con" if corrupcion["sha256_ok"] is False else "coincide con (¡error!)"), ""]

    md += ["## Tiempos (Python 3, computadora de desarrollo)", "",
           "| Archivo | Bits codificados | Bits/símbolo | Entropía | Comprimir | Descomprimir |", "|---|---|---|---|---|---|"]
    for _, r in resultados:
        md.append("| `%s` | %s | %.4f | %.4f | %.3f s | %.3f s |" % (r["nombre"], format(r["bits"], ","), r["prom"], r["h"],
                                                                  r["t_comp"], r["t_desc"]))
    md.append("")
    with open(os.path.join(AQUI, "RESULTADOS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))
    todo_ok = all(r["byte_a_byte"] and r["sha_ok"] for _, r in resultados) and corrupcion["sha256_ok"] is False
    print("\nTODAS LAS PRUEBAS:", "✔ PASARON" if todo_ok else "✘ FALLÓ ALGUNA")
    sys.exit(0 if todo_ok else 1)


if __name__ == "__main__":
    main()
