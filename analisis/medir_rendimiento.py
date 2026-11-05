"""
Mide el desempeño de Huffman (con los libros de la carpeta libros/) y de
Kruskal vs Prim (con grafos aleatorios de distintos tamaños).

Genera tablas en consola, un CSV y gráficas PNG en analisis/resultados/.
Requiere matplotlib solo para las gráficas:  pip install matplotlib

    python analisis/medir_rendimiento.py
"""
import csv
import glob
import os
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from huffman import (leer_texto, calcular_frecuencias, construir_arbol, generar_codigos, codificar,
                     guardar_comprimido, descomprimir_archivo, longitud_promedio, entropia, altura)
from mst import generar_grafo_aleatorio, kruskal, prim

SALIDA = os.path.join(RAIZ, "analisis", "resultados")


def medir_huffman():
    filas = []
    for ruta in sorted(glob.glob(os.path.join(RAIZ, "libros", "*.txt")), key=os.path.getsize):
        texto, cod = leer_texto(ruta)
        t0 = time.perf_counter()
        frec = calcular_frecuencias(texto)
        t1 = time.perf_counter()
        raiz, _ = construir_arbol(frec)
        codigos = generar_codigos(raiz)
        t2 = time.perf_counter()
        bits = codificar(texto, codigos)
        with tempfile.TemporaryDirectory() as tmp:
            huf = os.path.join(tmp, "x.huf")
            tam_huf = guardar_comprimido(huf, frec, bits, cod)
            t3 = time.perf_counter()
            recuperado = descomprimir_archivo(huf)
            t4 = time.perf_counter()
        original = os.path.getsize(ruta)
        filas.append({
            "libro": os.path.splitext(os.path.basename(ruta))[0],
            "caracteres": len(texto),
            "distintos": len(frec),
            "original_B": original,
            "huf_B": tam_huf,
            "ahorro_%": round((1 - tam_huf / original) * 100, 2),
            "bits_promedio": round(longitud_promedio(frec, codigos), 4),
            "entropia": round(entropia(frec), 4),
            "altura": altura(raiz),
            "t_frecuencias_s": round(t1 - t0, 4),
            "t_arbol_codigos_s": round(t2 - t1, 5),
            "t_codificar_s": round(t3 - t2, 4),
            "t_decodificar_s": round(t4 - t3, 4),
            "correcto": recuperado == texto,
        })
    return filas


def medir_mst(tamanos=(25, 50, 100, 200, 400, 800), repeticiones=3):
    filas = []
    for n in tamanos:
        tk = tp = 0.0
        aristas = 0
        for r in range(repeticiones):
            g = generar_grafo_aleatorio(n, densidad=0.5, semilla=1000 + r, ancho=3000, alto=3000)
            aristas += len(g.aristas)
            t0 = time.perf_counter()
            _, pk, _ = kruskal(g)
            t1 = time.perf_counter()
            _, pp, _ = prim(g)
            t2 = time.perf_counter()
            assert pk == pp
            tk += t1 - t0
            tp += t2 - t1
        filas.append({"nodos": n, "aristas": aristas // repeticiones,
                      "kruskal_ms": round(tk / repeticiones * 1000, 3),
                      "prim_ms": round(tp / repeticiones * 1000, 3)})
    return filas


def guardar_csv(nombre, filas):
    with open(os.path.join(SALIDA, nombre), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def imprimir(filas):
    claves = list(filas[0].keys())
    print(" | ".join(claves))
    for f in filas:
        print(" | ".join(str(f[k]) for k in claves))
    print()


def graficar(huf, mst):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no está instalado; se omiten las gráficas.")
        return

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    azul, coral, arena = "#1f2a44", "#e07a5f", "#f2cc8f"

    # 1) Tamaño original vs comprimido
    fig, ax = plt.subplots(figsize=(7, 3.6))
    nombres = [f["libro"].replace("_", " ") for f in huf]
    x = range(len(huf))
    ax.bar([i - 0.2 for i in x], [f["original_B"] / 1024 for f in huf], 0.4, label="Original", color=azul)
    ax.bar([i + 0.2 for i in x], [f["huf_B"] / 1024 for f in huf], 0.4, label="Comprimido (.huf)", color=coral)
    for i, f in enumerate(huf):
        ax.text(i + 0.2, f["huf_B"] / 1024, " -%.1f%%" % f["ahorro_%"], ha="center", va="bottom", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("KB (escala log)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(nombres, fontsize=9)
    ax.legend(frameon=False)
    ax.set_title("Tamaño original vs. comprimido con Huffman")
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "huffman_tamanos.png"), dpi=180)
    plt.close(fig)

    # 2) Tiempo de codificación/decodificación vs número de caracteres
    fig, ax = plt.subplots(figsize=(7, 3.4))
    n = [f["caracteres"] / 1e6 for f in huf]
    ax.plot(n, [f["t_codificar_s"] for f in huf], "o-", color=coral, label="Codificar + guardar")
    ax.plot(n, [f["t_decodificar_s"] for f in huf], "s-", color=azul, label="Leer + decodificar")
    ax.set_xlabel("Millones de caracteres del texto")
    ax.set_ylabel("Segundos")
    ax.set_title("Tiempo de ejecución de Huffman (crece de forma lineal)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "huffman_tiempos.png"), dpi=180)
    plt.close(fig)

    # 3) Kruskal vs Prim
    fig, ax = plt.subplots(figsize=(7, 3.4))
    e = [f["aristas"] for f in mst]
    ax.plot(e, [f["kruskal_ms"] for f in mst], "o-", color=coral, label="Kruskal  O(E log E)")
    ax.plot(e, [f["prim_ms"] for f in mst], "s-", color=azul, label="Prim con heap  O(E log V)")
    ax.set_xlabel("Número de aristas (E)")
    ax.set_ylabel("Milisegundos")
    ax.set_title("Árbol de expansión mínima: Kruskal vs. Prim")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "mst_tiempos.png"), dpi=180)
    plt.close(fig)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    print("== Huffman ==")
    huf = medir_huffman()
    imprimir(huf)
    guardar_csv("huffman.csv", huf)
    print("== Árbol de expansión mínima ==")
    mst = medir_mst()
    imprimir(mst)
    guardar_csv("mst.csv", mst)
    graficar(huf, mst)
    print("Resultados guardados en", SALIDA)


if __name__ == "__main__":
    main()
