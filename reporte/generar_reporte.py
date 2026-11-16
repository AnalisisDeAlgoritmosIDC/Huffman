"""
Genera reporte/Reporte_Huffman_MST.pdf con reportlab.

Antes de correrlo:
  1. python analisis/medir_rendimiento.py   (crea las tablas y gráficas)
  2. Ajusta los datos de la portada (INTEGRANTES, PROFESOR, etc.)

    pip install reportlab
    python reporte/generar_reporte.py
"""
import csv
import os
import sys
import zlib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from huffman import (calcular_frecuencias, construir_arbol, generar_codigos, codificar,
                     leer_texto, describir_caracter)

# ============================================================== DATOS DE PORTADA
UNIVERSIDAD = "Universidad de Guadalajara"
CENTRO = "Centro Universitario de Ciencias Exactas e Ingenierías"
MATERIA = "Análisis de Algoritmos"
PROFESOR = ""          # ej. "Mtro. Nombre Apellido"
SECCION = ""           # ej. "D05"
INTEGRANTES = [
    "Carlos Adrian Ramirez Gutiérrez",
    "Isaac Saldivar Zaldivar",
    "Daniel Padilla Echeverria",
]
FECHA = "5 de noviembre de 2026"
REPOSITORIO = "https://github.com/AnalisisDeAlgoritmosIDC/Huffman"
TITULO = "EL HUFFMANIFICADOR"
SUBTITULO = "Compresión de datos con el algoritmo de Huffman y Árbol de Expansión Mínima"

SALIDA = os.path.join(RAIZ, "reporte", "Reporte_Huffman_MST.pdf")
CAPTURAS = os.path.join(RAIZ, "capturas")
RESULTADOS = os.path.join(RAIZ, "analisis", "resultados")

# ============================================================== FUENTES
FUENTES = [
    ("Texto", ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
               "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]),
    ("Texto-B", ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]),
    ("Texto-I", ["C:/Windows/Fonts/ariali.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
                 "/Library/Fonts/Arial Italic.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"]),
    ("Mono", ["C:/Windows/Fonts/consola.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/Library/Fonts/Menlo.ttc"]),
]
RESPALDO = {"Texto": "Helvetica", "Texto-B": "Helvetica-Bold", "Texto-I": "Helvetica-Oblique", "Mono": "Courier"}
NOMBRE = {}
for alias, rutas in FUENTES:
    NOMBRE[alias] = RESPALDO[alias]
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                pdfmetrics.registerFont(TTFont(alias, ruta))
                NOMBRE[alias] = alias
                break
            except Exception:
                pass
if NOMBRE["Texto"] == "Texto":
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("Texto", normal="Texto", bold=NOMBRE["Texto-B"], italic=NOMBRE["Texto-I"],
                       boldItalic=NOMBRE["Texto-B"])

AZUL = colors.HexColor("#1f2a44")
CORAL = colors.HexColor("#e07a5f")
GRIS = colors.HexColor("#5b6478")
CLARO = colors.HexColor("#f4f1ea")

# ============================================================== ESTILOS
E = {
    "cuerpo": ParagraphStyle("cuerpo", fontName=NOMBRE["Texto"], fontSize=11, leading=16.5,
                             alignment=TA_JUSTIFY, spaceAfter=7),
    "h1": ParagraphStyle("h1", fontName=NOMBRE["Texto-B"], fontSize=16, leading=20, textColor=AZUL,
                         spaceBefore=6, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName=NOMBRE["Texto-B"], fontSize=12.5, leading=16, textColor=AZUL,
                         spaceBefore=10, spaceAfter=6),
    "vineta": ParagraphStyle("vineta", fontName=NOMBRE["Texto"], fontSize=11, leading=16, leftIndent=16,
                             bulletIndent=4, spaceAfter=3, alignment=TA_JUSTIFY),
    "pie": ParagraphStyle("pie", fontName=NOMBRE["Texto-I"], fontSize=9, leading=12, textColor=GRIS,
                          alignment=TA_CENTER, spaceBefore=4, spaceAfter=12),
    "codigo": ParagraphStyle("codigo", fontName=NOMBRE["Mono"], fontSize=8.8, leading=11.5,
                             backColor=CLARO, borderPadding=8, leftIndent=8, rightIndent=8,
                             spaceBefore=6, spaceAfter=12),
    "celda": ParagraphStyle("celda", fontName=NOMBRE["Texto"], fontSize=9, leading=11.5),
    "celda_b": ParagraphStyle("celda_b", fontName=NOMBRE["Texto-B"], fontSize=9, leading=11.5,
                              textColor=colors.white),
    "ref": ParagraphStyle("ref", fontName=NOMBRE["Texto"], fontSize=10.5, leading=15, leftIndent=24,
                          firstLineIndent=-24, spaceAfter=6),
    "portada": ParagraphStyle("portada", fontName=NOMBRE["Texto"], fontSize=12.5, leading=18, alignment=TA_CENTER),
    "toc1": ParagraphStyle("toc1", fontName=NOMBRE["Texto-B"], fontSize=11, leading=18, leftIndent=0),
    "toc2": ParagraphStyle("toc2", fontName=NOMBRE["Texto"], fontSize=10.5, leading=16, leftIndent=18),
}


class Documento(SimpleDocTemplate):
    """Registra los encabezados en el índice."""

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            nivel = 0 if f.style.name == "h1" else 1
            clave = "h%d" % id(f)
            self.canv.bookmarkPage(clave)
            self.notify("TOCEntry", (nivel, f.getPlainText(), self.page, clave))


def p(texto, estilo="cuerpo"):
    return Paragraph(texto, E[estilo])


def vinetas(lista):
    return [Paragraph(t, E["vineta"], bulletText="•") for t in lista]


def codigo(texto):
    return KeepTogether([Preformatted(texto.strip("\n"), E["codigo"])])


def tabla(datos, anchos, alinear_der=()):
    filas = [[Paragraph(str(c), E["celda_b"]) for c in datos[0]]]
    for fila in datos[1:]:
        filas.append([Paragraph(str(c), E["celda"]) for c in fila])
    t = Table(filas, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CLARO]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, AZUL),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(estilo))
    return t


def figura(nombre_archivo, pie, ancho=16.5 * cm, carpeta=CAPTURAS):
    ruta = os.path.join(carpeta, nombre_archivo)
    if not os.path.exists(ruta):
        return [p("<i>[Falta la imagen %s]</i>" % nombre_archivo)]
    img = Image(ruta)
    escala = ancho / img.imageWidth
    img.drawWidth, img.drawHeight = ancho, img.imageHeight * escala
    return [KeepTogether([img, Paragraph(pie, E["pie"])])]


def leer_csv(nombre):
    ruta = os.path.join(RESULTADOS, nombre)
    if not os.path.exists(ruta):
        return []
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def miles(n):
    return format(int(n), ",")


# ============================================================== PIE DE PÁGINA
def pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont(NOMBRE["Texto"], 8.5)
    canvas.setFillColor(GRIS)
    canvas.drawString(2.5 * cm, 1.4 * cm, "%s · %s" % (MATERIA, "El Huffmanificador"))
    canvas.drawRightString(letter[0] - 2.5 * cm, 1.4 * cm, str(doc.page))
    canvas.setStrokeColor(colors.HexColor("#c9c4b8"))
    canvas.line(2.5 * cm, 1.8 * cm, letter[0] - 2.5 * cm, 1.8 * cm)
    canvas.restoreState()


def portada(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, letter[1] - 1.2 * cm, letter[0], 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(CORAL)
    canvas.rect(0, letter[1] - 1.45 * cm, letter[0], 0.25 * cm, fill=1, stroke=0)
    canvas.restoreState()


# ============================================================== CONTENIDO
def construir():
    h = []

    # ---------------- Portada
    h.append(Spacer(1, 1.6 * cm))
    h.append(Paragraph(UNIVERSIDAD, ParagraphStyle("u", parent=E["portada"], fontName=NOMBRE["Texto-B"],
                                                   fontSize=17, leading=22)))
    h.append(Paragraph(CENTRO, E["portada"]))
    h.append(Spacer(1, 0.4 * cm))
    h.append(Paragraph(MATERIA + ((" · Sección " + SECCION) if SECCION else ""), E["portada"]))
    h.append(Spacer(1, 3.0 * cm))
    h.append(Paragraph(TITULO, ParagraphStyle("t", parent=E["portada"], fontName=NOMBRE["Texto-B"], fontSize=22,
                                              leading=28, textColor=AZUL)))
    h.append(Spacer(1, 0.4 * cm))
    h.append(Paragraph(SUBTITULO, ParagraphStyle("s", parent=E["portada"], textColor=CORAL, fontSize=13.5)))
    h.append(Spacer(1, 3.2 * cm))
    h.append(Paragraph("<b>Integrantes</b>", E["portada"]))
    for nombre in INTEGRANTES:
        h.append(Paragraph(nombre, E["portada"]))
    if PROFESOR:
        h.append(Spacer(1, 0.6 * cm))
        h.append(Paragraph("<b>Profesor</b>", E["portada"]))
        h.append(Paragraph(PROFESOR, E["portada"]))
    h.append(Spacer(1, 0.6 * cm))
    h.append(Paragraph('Repositorio: <link href="%s" color="#e07a5f">%s</link>' % (REPOSITORIO, REPOSITORIO.replace("https://", "")),
                       E["portada"]))
    h.append(Spacer(1, 1.0 * cm))
    h.append(Paragraph("Guadalajara, Jalisco · " + FECHA, E["portada"]))
    h.append(PageBreak())

    # ---------------- Índice
    h.append(Paragraph("Índice", ParagraphStyle("indice", parent=E["h1"])))
    toc = TableOfContents()
    toc.levelStyles = [E["toc1"], E["toc2"]]
    toc.dotsMinLevel = 0
    h.append(toc)
    h.append(PageBreak())

    # ---------------- Datos calculados
    libros = leer_csv("huffman.csv")
    mst = leer_csv("mst.csv")
    alice = os.path.join(RAIZ, "libros", "alice_in_wonderland.txt")
    with open(alice, "rb") as f:
        bytes_alice = f.read()
    zlib_alice = len(zlib.compress(bytes_alice, 9))
    texto_alice, cod_alice = leer_texto(alice)
    frec_alice = calcular_frecuencias(texto_alice)
    bits_alice = codificar(texto_alice, generar_codigos(construir_arbol(frec_alice)[0]))
    encabezado_alice = 4 + 1 + len(cod_alice) + 4 + 1 + sum(1 + len(c.encode("utf-8")) + 4 for c in frec_alice)
    huf_alice = encabezado_alice + (len(bits_alice) + 7) // 8

    ejemplo = "abracadabra"
    frec_ej = calcular_frecuencias(ejemplo)
    raiz_ej, pasos_ej = construir_arbol(frec_ej)
    cod_ej = generar_codigos(raiz_ej)
    bits_ej = codificar(ejemplo, cod_ej)

    # ---------------- 1. Introducción
    h.append(p("1. Introducción", "h1"))
    h.append(p(
        "Los <b>algoritmos voraces</b> (<i>greedy</i>) resuelven un problema de optimización tomando, en cada "
        "paso, la decisión que parece mejor en ese momento, sin reconsiderar decisiones anteriores. No todos "
        "los problemas admiten esta estrategia, pero cuando el problema cumple la <i>propiedad de elección "
        "voraz</i> y tiene <i>subestructura óptima</i>, el resultado es una solución óptima obtenida de forma "
        "muy eficiente."))
    h.append(p(
        "En este proyecto se estudian dos de los ejemplos clásicos de esta técnica. El primero es el "
        "<b>algoritmo de Huffman</b> (1952), que construye un código binario de longitud variable óptimo para "
        "comprimir datos: a los caracteres más frecuentes les asigna códigos cortos y a los menos frecuentes "
        "códigos largos. El segundo es el problema del <b>árbol de expansión mínima</b> (<i>Minimum Spanning "
        "Tree</i>, MST), resuelto con los algoritmos de <b>Kruskal</b> y <b>Prim</b>, que conectan todos los "
        "vértices de un grafo ponderado con el menor costo total posible."))
    h.append(p(
        "Ambos algoritmos se implementaron en Python y se presentan en una <b>página web</b>, «El "
        "Huffmanificador», que sirve como interfaz gráfica: el código de Python se ejecuta directamente en el "
        "navegador mediante Pyodide (Python compilado a WebAssembly). La página incluye un buscador conectado a "
        "Project Gutenberg para elegir el libro a comprimir, mide el tamaño del archivo original y del "
        "comprimido (extensión .mc), verifica que la decodificación reproduzca el texto exactamente y, además, "
        "detecta el idioma del libro."))

    # ---------------- 2. Objetivos
    h.append(p("2. Objetivos", "h1"))
    h.append(p("2.1 Objetivo general", "h2"))
    h.append(p(
        "Implementar y analizar el algoritmo de Huffman, que utiliza la técnica voraz para la compresión de "
        "datos, a través de la construcción de un árbol binario óptimo basado en la frecuencia de aparición de "
        "caracteres; e implementar un algoritmo de árbol de expansión mínima como segundo caso de estudio de "
        "la misma técnica."))
    h.append(p("2.2 Objetivos específicos", "h2"))
    h.extend(vinetas([
        "Leer un archivo de texto (.txt) y calcular la frecuencia de aparición de cada carácter.",
        "Construir el árbol de Huffman con una cola de prioridad aplicando la elección voraz.",
        "Generar los códigos binarios asociados a cada carácter.",
        "Codificar y decodificar el contenido del archivo con los códigos generados.",
        "Comparar el tamaño del archivo original con el del archivo codificado para evaluar la compresión.",
        "Implementar los algoritmos de Kruskal y Prim para obtener el árbol de expansión mínima de un grafo.",
        "Presentar todo el funcionamiento mediante una interfaz gráfica (GUI) en forma de página web.",
        "Detectar automáticamente el idioma del libro analizado.",
    ]))

    # ---------------- 3. Marco teórico
    h.append(p("3. Marco teórico", "h1"))
    h.append(p("3.1 Técnica voraz", "h2"))
    h.append(p(
        "Un algoritmo voraz construye la solución por partes. En cada iteración elige, de entre los candidatos "
        "disponibles, el que optimiza un criterio local (el más barato, el más ligero, el menos frecuente, "
        "etc.) y lo incorpora a la solución de forma definitiva. Para demostrar que una estrategia voraz es "
        "correcta se deben probar dos propiedades (Cormen et al., 2009):"))
    h.extend(vinetas([
        "<b>Propiedad de elección voraz:</b> existe una solución óptima que incluye la elección local hecha "
        "por el algoritmo.",
        "<b>Subestructura óptima:</b> después de hacer la elección, el subproblema restante también se "
        "resuelve de manera óptima con la misma estrategia.",
    ]))

    h.append(p("3.2 Compresión de datos y códigos prefijo", "h2"))
    h.append(p(
        "Un archivo de texto normalmente almacena cada carácter con un número fijo de bits (8 bits en ASCII o "
        "Latin-1). Esto desperdicia espacio porque los caracteres no aparecen con la misma frecuencia: en un "
        "texto en inglés el espacio y la letra <i>e</i> son mucho más comunes que la <i>z</i> o la <i>q</i>. "
        "Un <b>código de longitud variable</b> aprovecha esta diferencia."))
    h.append(p(
        "Para poder decodificar sin separadores, el código debe ser un <b>código prefijo</b>: ningún código es "
        "prefijo de otro. Así, al leer los bits de izquierda a derecha, en cuanto se completa un código válido "
        "se sabe con certeza a qué carácter corresponde. Todo código prefijo puede representarse como un árbol "
        "binario cuyas hojas son los caracteres; el camino de la raíz a una hoja (0 = izquierda, 1 = derecha) "
        "es su código."))
    h.append(p(
        "El costo de un árbol T para un texto es el número total de bits que produce: "
        "B(T) = Σ f(c) · d<sub>T</sub>(c), donde f(c) es la frecuencia del carácter c y d<sub>T</sub>(c) su "
        "profundidad en el árbol (la longitud de su código). El problema es encontrar el árbol que minimiza "
        "B(T)."))

    h.append(p("3.3 Algoritmo de Huffman", "h2"))
    h.append(p(
        "David A. Huffman (1952) demostró que el siguiente procedimiento voraz produce un código prefijo "
        "óptimo: se crea una hoja por cada carácter con su frecuencia y se colocan en una cola de prioridad "
        "mínima; mientras haya más de un nodo, se extraen los <b>dos nodos de menor frecuencia</b>, se unen "
        "como hijos de un nuevo nodo cuya frecuencia es la suma de ambos, y el nuevo nodo se inserta de nuevo "
        "en la cola. El último nodo es la raíz del árbol."))
    h.append(codigo("""
HUFFMAN(C)                         // C = conjunto de caracteres con frecuencia f
  n <- |C|
  Q <- cola de prioridad mínima con los elementos de C
  para i <- 1 hasta n - 1
      z <- nuevo nodo
      z.izq <- x <- EXTRAER-MIN(Q)       // elección voraz
      z.der <- y <- EXTRAER-MIN(Q)       // elección voraz
      z.f   <- x.f + y.f
      INSERTAR(Q, z)
  regresar EXTRAER-MIN(Q)          // raíz del árbol
"""))
    h.append(p(
        "<b>Justificación de la elección voraz.</b> Los dos caracteres menos frecuentes x e y pueden ubicarse "
        "como hermanos en el nivel más profundo de algún árbol óptimo: si no lo estuvieran, intercambiarlos "
        "con las hojas más profundas no aumentaría el costo. Al fusionarlos en un solo símbolo de frecuencia "
        "f(x)+f(y) el problema se reduce a uno con n−1 símbolos que se resuelve con la misma estrategia "
        "(subestructura óptima)."))
    h.append(p(
        "<b>Complejidad.</b> Con un heap binario, construir la cola cuesta O(n) y cada una de las n−1 "
        "iteraciones hace operaciones O(log n), por lo que construir el árbol es <b>O(n log n)</b>, donde n es "
        "el número de caracteres <i>distintos</i>. Contar frecuencias, codificar y decodificar recorren el "
        "texto una vez, así que son <b>O(N)</b> en la longitud N del texto (la decodificación hace un paso por "
        "bit, O(N · L) con L la longitud promedio del código, que es acotada)."))

    h.append(p("<b>Ejemplo.</b> Para la cadena «%s» las frecuencias son %s. El algoritmo realiza las "
               "siguientes uniones voraces:" % (ejemplo, ", ".join("%s = %d" % (c, f) for c, f in
                                                                    sorted(frec_ej.items(), key=lambda x: -x[1]))),
               ))

    def nombre_nodo(n):
        return "'%s' (%d)" % (n.caracter, n.frecuencia) if n.es_hoja() else "nodo (%d)" % n.frecuencia

    filas = [["Paso", "Nodo menor", "Segundo menor", "Nuevo nodo"]]
    for i, (a, b, padre) in enumerate(pasos_ej, 1):
        filas.append([i, nombre_nodo(a), nombre_nodo(b), padre.frecuencia])
    h.append(tabla(filas, [2 * cm, 4.6 * cm, 4.6 * cm, 3.4 * cm]))
    h.append(Spacer(1, 8))
    filas = [["Carácter", "Frecuencia", "Código", "Bits × frecuencia"]]
    for c, f in sorted(frec_ej.items(), key=lambda x: (-x[1], x[0])):
        filas.append([c, f, cod_ej[c], "%d × %d = %d" % (len(cod_ej[c]), f, len(cod_ej[c]) * f)])
    h.append(tabla(filas, [3 * cm, 3 * cm, 3.4 * cm, 5.2 * cm]))
    h.append(Spacer(1, 8))
    h.append(p(
        "La cadena codificada ocupa <b>%d bits</b> (%s), contra %d bits con un código fijo de 8 bits por "
        "carácter, o %d bits con el mejor código de longitud fija posible (3 bits para 5 símbolos)." % (
            len(bits_ej), bits_ej, len(ejemplo) * 8, len(ejemplo) * 3)))

    h.append(p("3.4 Entropía de Shannon", "h2"))
    h.append(p(
        "Shannon (1948) mostró que ningún código sin pérdida que codifique carácter por carácter puede usar, en "
        "promedio, menos bits que la <b>entropía</b> de la fuente: H = −Σ p<sub>i</sub> log<sub>2</sub> "
        "p<sub>i</sub>, donde p<sub>i</sub> es la probabilidad de cada carácter. El código de Huffman cumple "
        "H ≤ L &lt; H + 1, donde L es su longitud promedio en bits por carácter. La razón H / L se usa en este "
        "trabajo como <i>eficiencia</i> del código."))

    h.append(p("3.5 Árbol de expansión mínima", "h2"))
    h.append(p(
        "Dado un grafo conexo, no dirigido y ponderado G = (V, E), un <b>árbol de expansión</b> es un "
        "subconjunto de |V|−1 aristas que conecta todos los vértices sin formar ciclos. El <b>árbol de "
        "expansión mínima</b> es el de menor suma de pesos. Tiene aplicaciones en el diseño de redes "
        "(eléctricas, de telecomunicaciones, de tuberías), en agrupamiento (<i>clustering</i>) y como "
        "subrutina de aproximación para otros problemas. Ambos algoritmos se basan en la <b>propiedad del "
        "corte</b>: para cualquier partición de los vértices en dos conjuntos, la arista más ligera que cruza "
        "el corte pertenece a algún árbol de expansión mínima."))
    h.append(p("<b>Algoritmo de Kruskal (1956).</b> Ordena todas las aristas por peso y las recorre de la más "
               "ligera a la más pesada; acepta una arista solo si une dos componentes distintas (no forma "
               "ciclo). Para verificarlo eficientemente usa la estructura <i>Union-Find</i> (conjuntos "
               "disjuntos) con compresión de caminos y unión por rango. Complejidad: <b>O(E log E)</b>, "
               "dominada por el ordenamiento."))
    h.append(codigo("""
KRUSKAL(G)
  A <- {}
  para cada vértice v: CREAR-CONJUNTO(v)
  ordenar E por peso ascendente
  para cada arista (u, v) en ese orden
      si ENCONTRAR(u) != ENCONTRAR(v)     // no forma ciclo
          A <- A ∪ {(u, v)}
          UNIR(u, v)
  regresar A
"""))
    h.append(p("<b>Algoritmo de Prim (1957).</b> Parte de un vértice inicial y hace crecer un solo árbol: en "
               "cada paso agrega la arista más ligera que conecta un vértice del árbol con uno de fuera. Con "
               "una cola de prioridad (heap binario) la complejidad es <b>O(E log V)</b>. La versión "
               "implementada es la «perezosa»: inserta aristas en el heap y descarta las que llevan a un "
               "vértice ya visitado al momento de extraerlas."))
    h.append(codigo("""
PRIM(G, r)
  visitado[r] <- verdadero
  Q <- heap con las aristas que salen de r
  mientras Q no esté vacío y |A| < |V| - 1
      (w, u, v) <- EXTRAER-MIN(Q)          // elección voraz
      si visitado[v]: continuar            // arista descartada
      visitado[v] <- verdadero
      A <- A ∪ {(u, v)}
      insertar en Q las aristas (v, x) con x no visitado
  regresar A
"""))

    # ---------------- 4. Desarrollo
    h.append(p("4. Desarrollo e implementación", "h1"))
    h.append(p("4.1 Herramientas", "h2"))
    h.extend(vinetas([
        "<b>Lenguaje:</b> Python 3 (compatible desde la versión 3.8).",
        "<b>Interfaz gráfica:</b> página web en HTML, CSS y JavaScript. Los algoritmos de Python se ejecutan "
        "en el navegador con <b>Pyodide</b> (CPython compilado a WebAssembly); JavaScript solo dibuja la interfaz.",
        "<b>Servidor:</b> un Cloudflare Worker publica la página y funciona como intermediario con "
        "gutenberg.org para buscar y descargar libros (Gutenberg no permite que otras páginas lean sus "
        "archivos directamente desde el navegador).",
        "<b>Estructuras de datos:</b> <font face='%s'>heapq</font> para las colas de prioridad, "
        "<font face='%s'>collections.Counter</font> para las frecuencias y Union-Find propio para Kruskal."
        % (NOMBRE["Mono"], NOMBRE["Mono"]),
        "<b>Pruebas:</b> <font face='%s'>unittest</font> (14 pruebas: casos límite, ida y vuelta del "
        "archivo, Kruskal y Prim contra fuerza bruta y detección de idioma en seis idiomas)." % NOMBRE["Mono"],
        "<b>Control de versiones:</b> Git y GitHub, con el trabajo dividido entre los tres integrantes "
        "(repositorio: %s)." % REPOSITORIO,
        "<b>Datos:</b> libros de dominio público de Project Gutenberg.",
    ]))
    h.append(p("4.2 Estructura del proyecto", "h2"))
    h.append(codigo("""
index.html              página web (El Huffmanificador)
huffman/
  frecuencias.py        leer el .txt y contar caracteres
  arbol.py              clase Nodo y construcción voraz del árbol
  codigos.py            recorrido del árbol -> tabla de códigos
  codificador.py        codificar / decodificar y formato .mc
  estadisticas.py       longitud promedio, entropía, razón de compresión
mst/
  grafo.py              grafo ponderado y generador aleatorio conexo
  kruskal.py            Kruskal + Union-Find
  prim.py               Prim con heap
idioma/
  detector.py           detección de idioma por palabras vacías
web/
  puente.py             funciones de Python que llama la página
  python.js             carga Pyodide y los módulos .py
  huffman_ui.js, arbol.js, arbol_radial.js, construccion.js,
  ahorro.js, idioma_ui.js, mst_ui.js, buscador.js, app.js
                        interfaz de cada sección
  styles.css            estilos
worker/index.js         servidor: búsqueda y descarga en Gutenberg
tests/                  pruebas unitarias
analisis/               medición de rendimiento y gráficas
"""))
    h.append(p("4.3 Flujo de compresión", "h2"))
    h.extend(vinetas([
        "<b>Lectura:</b> el archivo se lee en modo binario y se decodifica como UTF-8 (o Latin-1 si falla). "
        "Leer en binario conserva los saltos de línea exactamente como están (\\r\\n o \\n), lo que permite "
        "una reconstrucción idéntica byte por byte.",
        "<b>Frecuencias:</b> <font face='%s'>Counter(texto)</font> recorre el texto una vez." % NOMBRE["Mono"],
        "<b>Árbol:</b> las hojas se insertan al heap ordenadas por (frecuencia, carácter) y se desempatan con "
        "un contador; así el árbol es determinista y el descompresor puede reconstruir exactamente el mismo "
        "árbol a partir de la tabla de frecuencias.",
        "<b>Códigos:</b> recorrido iterativo con pila; izquierda agrega «0» y derecha «1». Si el texto solo "
        "tiene un carácter distinto se le asigna el código «0».",
        "<b>Codificación:</b> se concatenan los códigos y la cadena de bits se empaqueta en bytes; se guarda "
        "cuántos bits de relleno tiene el último byte.",
        "<b>Decodificación:</b> se recorre el árbol bit por bit desde la raíz; al llegar a una hoja se emite "
        "su carácter y se regresa a la raíz.",
    ]))
    h.append(p("4.4 Formato del archivo comprimido (.mc)", "h2"))
    h.append(p("El archivo comprimido debe incluir la información necesaria para reconstruir el árbol. Se "
               "eligió guardar la tabla de frecuencias, que es compacta y permite repetir la construcción "
               "voraz de forma determinista:"))
    h.append(tabla([
        ["Campo", "Tamaño", "Descripción"],
        ["Firma", "4 bytes", "«HMC1», identifica el formato"],
        ["Codificación", "1 + n bytes", "Nombre de la codificación del texto original (utf-8 / latin-1)"],
        ["K", "4 bytes", "Número de caracteres distintos"],
        ["Tabla", "K × (1 + 1..4 + 4) bytes", "Para cada carácter: largo en UTF-8, el carácter y su frecuencia"],
        ["Relleno", "1 byte", "Bits de relleno agregados al último byte (0 a 7)"],
        ["Datos", "⌈bits / 8⌉ bytes", "Texto codificado con Huffman"],
    ], [3 * cm, 4.2 * cm, 9.3 * cm]))
    h.append(Spacer(1, 6))
    h.append(p("4.5 Interfaz gráfica: la página web", "h2"))
    h.append(p(
        "Al abrir la página se descarga Pyodide y se cargan los mismos archivos de Python del proyecto "
        "(<font face='%s'>huffman/</font>, <font face='%s'>mst/</font>, <font face='%s'>idioma/</font>). "
        "El archivo <font face='%s'>web/puente.py</font> expone las funciones que llama la página "
        "(analizar, comprimir, descomprimir y generar grafos) y regresa sus resultados en JSON, que JavaScript "
        "solo se encarga de dibujar." % (NOMBRE["Mono"], NOMBRE["Mono"], NOMBRE["Mono"], NOMBRE["Mono"])))
    h.extend(vinetas([
        "<b>Entrada de datos:</b> buscador de Project Gutenberg por título o autor con filtro de idioma, o "
        "arrastrar un .txt propio. También se puede soltar un .mc para decodificarlo.",
        "<b>Métricas:</b> tamaño original y comprimido, porcentaje de ahorro, entropía, idioma detectado y "
        "verificación byte por byte; botones para codificar, decodificar y descargar el .mc y el .txt.",
        "<b>Árbol en cuatro vistas:</b> jerárquica, radial (cada círculo es un bit más de código), "
        "explorador desplegable y construcción paso a paso, que anima la cola de prioridad y resalta los dos "
        "nodos de menor frecuencia que se unen en cada paso.",
        "<b>Tabla de frecuencias y códigos:</b> con filtro; al seleccionar un carácter se resalta su camino "
        "en el árbol.",
        "<b>Ahorro interactivo:</b> curva de bits acumulados (original contra Huffman) que se recorre con el "
        "mouse, vista carácter por carácter con sus bits, los caracteres que más ahorran o cuestan y una "
        "calculadora para varios libros.",
        "<b>Bitstream y decodificador:</b> la cadena de bits generada y el texto reconstruido.",
        "<b>Árbol de expansión mínima:</b> grafo aleatorio conexo (nodos, densidad y semilla configurables); "
        "Kruskal o Prim completo, paso a paso o animado, con una bitácora de cada arista aceptada o rechazada.",
    ]))
    h.append(p("4.6 Detección de idioma", "h2"))
    h.append(p(
        "El módulo <font face='%s'>idioma/detector.py</font> cuenta las <b>palabras vacías</b> (artículos, "
        "preposiciones y conjunciones) de ocho idiomas: español, inglés, francés, alemán, italiano, portugués, "
        "neerlandés y latín. Estas palabras forman cerca de la mitad de cualquier texto, así que el idioma con "
        "más coincidencias es el del libro. Como varios idiomas comparten palabras (por ejemplo «de» o «la»), "
        "cada palabra vale 1/k si aparece en k idiomas, y las letras características (ñ, ç, ß, ã…) suman un "
        "pequeño puntaje adicional. Antes de analizar se quita el encabezado y la licencia de Project "
        "Gutenberg, que siempre están en inglés, y se compara el resultado con el campo «Language» del libro."
        % NOMBRE["Mono"]))

    # ---------------- 5. Resultados
    h.append(PageBreak())
    h.append(p("5. Resultados y capturas del funcionamiento", "h1"))
    h.append(p("5.1 Compresión de Huffman", "h2"))
    h.append(p("Se usó como libro principal <i>Alice's Adventures in Wonderland</i> de Lewis Carroll (Project "
               "Gutenberg, libro #11), elegido con el buscador de la página. Las siguientes capturas muestran "
               "cada sección de la interfaz."))
    h += figura("01_huffman_libro_y_metricas.png",
                "Figura 1. Búsqueda en Project Gutenberg y métricas: 141.01 KB → 81.29 KB (42.35 % de ahorro), "
                "idioma inglés y archivo decodificado idéntico al original.")
    h += figura("02_huffman_frecuencias_codigos.png",
                "Figura 2. Tabla de frecuencias y códigos: el espacio y la «e» reciben códigos de solo 3 bits.")
    h += figura("03_huffman_arbol_jerarquico.png",
                "Figura 3. Vista jerárquica del árbol; al seleccionar «e» (código 000) se resalta su camino.")
    h += figura("04_huffman_arbol_radial.png",
                "Figura 4. Vista radial: los caracteres frecuentes quedan cerca del centro (códigos cortos).")
    h += figura("05_huffman_arbol_explorador.png",
                "Figura 5. Vista de explorador: el árbol como ramas desplegables con el código de cada hoja.")
    h += figura("06_huffman_construccion_paso_a_paso.png",
                "Figura 6. Construcción paso a paso: la cola de prioridad y los dos nodos de menor frecuencia "
                "que se unen en el siguiente paso voraz.")
    h += figura("07_huffman_ahorro_interactivo.png",
                "Figura 7. Ahorro interactivo: ahorro total, calculadora, curva de bits acumulados, vista "
                "carácter por carácter y caracteres que más ahorran.", ancho=13.5 * cm)
    h += figura("09_huffman_bitstream_decodificado.png",
                "Figura 8. Bitstream generado y decodificador: el texto se reconstruye recorriendo el árbol "
                "bit por bit.")
    h += figura("10_huffman_resultados.png",
                "Figura 9. Resultados de compresión y comparación de tamaños.")

    h.append(p("5.2 Detección de idioma", "h2"))
    h.append(p("La página detecta el idioma de cada libro al analizarlo. Con <i>Alice</i> el resultado es inglés "
               "y coincide con el idioma que declara Project Gutenberg; con un texto en español (fragmento de "
               "<i>Don Quijote</i>) el resultado es español."))
    h += figura("08_idioma_detectado.png", "Figura 10. Idioma detectado para Alice: inglés, con las palabras "
                "que lo delatan («the», «and», «to»…).")
    h += figura("11_idioma_espanol.png", "Figura 11. Idioma detectado para un texto en español.")

    if libros:
        h.append(p("5.3 Comparación con varios libros", "h2"))
        h.append(p("Para evaluar el comportamiento con textos de distinto tamaño se procesaron cuatro libros de "
                   "Project Gutenberg con el script <font face='%s'>analisis/medir_rendimiento.py</font>:"
                   % NOMBRE["Mono"]))
        filas = [["Libro", "Caracteres", "Distintos", "Original", ".mc", "Ahorro", "Bits/car.", "Entropía"]]
        for f in libros:
            filas.append([f["libro"].replace("_", " "), miles(f["caracteres"]), f["distintos"],
                          "%.1f KB" % (int(f["original_B"]) / 1024), "%.1f KB" % (int(f["huf_B"]) / 1024),
                          "%s %%" % f["ahorro_%"], f["bits_promedio"], f["entropia"]])
        h.append(tabla(filas, [3.4 * cm, 2 * cm, 1.6 * cm, 2 * cm, 2 * cm, 1.7 * cm, 1.6 * cm, 1.6 * cm]))
        h.append(Spacer(1, 8))
        h += figura("huffman_tamanos.png", "Figura 12. Tamaño original contra tamaño comprimido (escala logarítmica).",
                    ancho=14.5 * cm, carpeta=RESULTADOS)
        filas = [["Libro", "Frecuencias", "Árbol + códigos", "Codificar + guardar", "Leer + decodificar"]]
        for f in libros:
            filas.append([f["libro"].replace("_", " "), "%s s" % f["t_frecuencias_s"],
                          "%s s" % f["t_arbol_codigos_s"], "%s s" % f["t_codificar_s"],
                          "%s s" % f["t_decodificar_s"]])
        h.append(tabla(filas, [3.8 * cm, 2.6 * cm, 3 * cm, 3.4 * cm, 3.4 * cm]))
        h.append(Spacer(1, 8))
        h += figura("huffman_tiempos.png", "Figura 13. Tiempos de codificación y decodificación según el tamaño "
                    "del texto.", ancho=14.5 * cm, carpeta=RESULTADOS)

    h.append(p("5.4 Árbol de expansión mínima", "h2"))
    h += figura("12_mst_kruskal_paso_a_paso.png",
                "Figura 14. Kruskal paso a paso: en el paso 7 la arista C–N se rechaza porque formaría un ciclo.")
    h += figura("13_mst_kruskal_final.png",
                "Figura 15. Resultado de Kruskal: 13 aristas (n − 1) con peso total 135.")
    h += figura("14_mst_prim_paso_a_paso.png",
                "Figura 16. Prim paso a paso desde el nodo A: el árbol crece desde un solo vértice.")
    h += figura("15_mst_prim_final.png",
                "Figura 17. Resultado de Prim sobre el mismo grafo: mismo peso total (135).")
    h += figura("16_mst_grafo_grande.png",
                "Figura 18. Grafo de 30 nodos: 71 aristas evaluadas, 42 rechazadas por formar ciclo, peso 222.")
    if mst:
        filas = [["Nodos (V)", "Aristas (E)", "Kruskal (ms)", "Prim (ms)"]]
        for f in mst:
            filas.append([f["nodos"], f["aristas"], f["kruskal_ms"], f["prim_ms"]])
        h.append(tabla(filas, [3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]))
        h.append(Spacer(1, 8))
        h += figura("mst_tiempos.png", "Figura 19. Tiempo de Kruskal y Prim en grafos aleatorios (promedio de 3 "
                    "corridas).", ancho=14.5 * cm, carpeta=RESULTADOS)

    # ---------------- 6. Análisis
    h.append(p("6. Análisis de resultados", "h1"))
    if libros:
        prom_ahorro = sum(float(f["ahorro_%"]) for f in libros) / len(libros)
        ef = [float(f["entropia"]) / float(f["bits_promedio"]) * 100 for f in libros]
        h.append(p(
            "<b>Eficiencia de la compresión.</b> En los cuatro libros el ahorro fue muy estable, de %.1f %% en "
            "promedio. La razón es que los cuatro son textos en inglés con un alfabeto parecido (entre 67 y 82 "
            "caracteres distintos) y distribuciones de frecuencia similares: Huffman reduce los 8 bits por "
            "carácter del archivo original a unos 4.6 bits en promedio. Esa longitud promedio queda a menos "
            "de 0.05 bits de la entropía de Shannon (eficiencia entre %.1f %% y %.1f %%), lo que confirma "
            "experimentalmente que el código es prácticamente óptimo para una codificación carácter por "
            "carácter." % (prom_ahorro, min(ef), max(ef))))
    h.append(p(
        "<b>Costo del encabezado.</b> El archivo .mc incluye la tabla de frecuencias (unos 9 bytes por "
        "carácter distinto). En <i>Alice</i> esto representa solo %s bytes de los %s del archivo, por lo que "
        "su efecto es despreciable en textos grandes; en archivos muy pequeños, en cambio, el encabezado puede "
        "hacer que el archivo «comprimido» sea más grande que el original." % (
            miles(encabezado_alice), miles(huf_alice))))
    h.append(p(
        "<b>Tiempo de ejecución.</b> Construir el árbol tarda menos de un milisegundo aun para la Biblia "
        "(4.3 millones de caracteres), porque solo depende del número de caracteres distintos (≈ 75), no del "
        "tamaño del texto. Las etapas que sí recorren el texto (contar, codificar y decodificar) crecen de forma "
        "lineal, como se observa en la Figura 13. La decodificación es la etapa más lenta porque procesa el "
        "archivo bit por bit dentro de un ciclo de Python."))
    h.append(p(
        "<b>Comparación con otros compresores.</b> Como referencia, el algoritmo DEFLATE (el de ZIP, vía "
        "<font face='%s'>zlib</font> nivel 9) reduce <i>Alice</i> a %s bytes (%.1f %% de ahorro) contra %s "
        "bytes de Huffman. DEFLATE combina LZ77, que sustituye palabras y frases repetidas por referencias, con "
        "un código de Huffman. Esto muestra la principal limitación de Huffman por sí solo: considera cada "
        "carácter de forma independiente y no aprovecha el contexto ni las repeticiones." % (
            NOMBRE["Mono"], miles(zlib_alice), (1 - zlib_alice / len(bytes_alice)) * 100,
            miles(huf_alice))))
    h.append(p(
        "<b>Árbol de expansión mínima.</b> Kruskal y Prim obtuvieron siempre el mismo peso total (se verificó "
        "con 30 grafos aleatorios en las pruebas y con un algoritmo de fuerza bruta en grafos pequeños). "
        "Los árboles pueden diferir cuando hay aristas con el mismo peso, pero el costo mínimo es único. En "
        "los grafos generados (dispersos, E ≈ 2.3 V) Kruskal resultó ligeramente más rápido; Prim con heap "
        "conviene más en grafos densos o cuando el grafo ya está en lista de adyacencia, y Kruskal cuando las "
        "aristas ya vienen ordenadas o el grafo es disperso."))
    h.append(p(
        "<b>Relación entre ambos problemas.</b> Los tres algoritmos comparten el mismo esquema: una cola de "
        "prioridad o un ordenamiento que entrega el candidato «más barato», una regla para decidir si ese "
        "candidato es válido y una decisión que nunca se deshace. La diferencia está en el criterio: Huffman "
        "combina los dos símbolos menos frecuentes, Kruskal toma la arista más ligera que no forma ciclo y "
        "Prim la arista más ligera que sale del árbol actual."))

    # ---------------- 7. Conclusiones
    h.append(p("7. Conclusiones", "h1"))
    h.append(p(
        "Se implementó el algoritmo de Huffman completo: lectura del archivo, conteo de frecuencias, "
        "construcción voraz del árbol con un heap, generación de códigos, codificación a un archivo binario "
        "propio y decodificación que recupera el texto idéntico byte por byte. Con libros de Project Gutenberg "
        "se obtuvo un ahorro de alrededor del 42 %, con una longitud promedio de código prácticamente igual a "
        "la entropía de Shannon, lo que comprueba en la práctica que la elección voraz produce un código "
        "óptimo."))
    h.append(p(
        "También se implementaron Kruskal y Prim para el árbol de expansión mínima, que llegan al mismo costo "
        "por caminos distintos. Ver los tres algoritmos en la página web, paso por paso, ayuda a entender "
        "por qué la técnica voraz funciona: cada decisión local es segura porque cumple una propiedad (la de "
        "los dos menos frecuentes en Huffman, la del corte en el MST) que garantiza que no se pierde la "
        "solución óptima."))
    h.append(p(
        "Presentar el proyecto como página web permitió que los mismos módulos de Python se usen sin instalar "
        "nada: el navegador ejecuta Python con Pyodide, el buscador trae los libros directamente de Project "
        "Gutenberg y la detección de idioma identifica el texto antes de comprimirlo."))
    h.append(p(
        "Finalmente, el análisis muestra los límites del método: Huffman es óptimo entre los códigos que "
        "asignan una palabra fija a cada carácter, pero compresores como ZIP logran más al explotar "
        "repeticiones de secuencias. Como trabajo futuro se podría aplicar Huffman sobre palabras o pares de "
        "caracteres, o combinarlo con LZ77 para acercarse a DEFLATE."))

    # ---------------- 8. Referencias
    h.append(p("8. Referencias", "h1"))
    for r in [
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., &amp; Stein, C. (2009). <i>Introduction to "
        "algorithms</i> (3.ª ed.). MIT Press. (Cap. 16: Greedy Algorithms; Cap. 23: Minimum Spanning Trees).",
        "Huffman, D. A. (1952). A method for the construction of minimum-redundancy codes. <i>Proceedings of "
        "the IRE, 40</i>(9), 1098–1101. https://doi.org/10.1109/JRPROC.1952.273898",
        "Kruskal, J. B. (1956). On the shortest spanning subtree of a graph and the traveling salesman "
        "problem. <i>Proceedings of the American Mathematical Society, 7</i>(1), 48–50.",
        "Prim, R. C. (1957). Shortest connection networks and some generalizations. <i>Bell System Technical "
        "Journal, 36</i>(6), 1389–1401.",
        "Shannon, C. E. (1948). A mathematical theory of communication. <i>Bell System Technical Journal, "
        "27</i>(3), 379–423.",
        "Sedgewick, R., &amp; Wayne, K. (2011). <i>Algorithms</i> (4.ª ed.). Addison-Wesley.",
        "Carroll, L. (1865). <i>Alice's adventures in Wonderland</i>. Project Gutenberg. "
        "https://www.gutenberg.org/ebooks/11",
        "Python Software Foundation. (2024). <i>heapq — Heap queue algorithm</i>. "
        "https://docs.python.org/3/library/heapq.html",
        "Pyodide contributors. (2024). <i>Pyodide: Python distribution for the browser based on "
        "WebAssembly</i> (versión 0.26). https://pyodide.org",
        "Cloudflare. (2025). <i>Cloudflare Workers documentation</i>. https://developers.cloudflare.com/workers/",
    ]:
        h.append(Paragraph(r, E["ref"]))

    return h


def main():
    doc = Documento(SALIDA, pagesize=letter, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                    topMargin=2.5 * cm, bottomMargin=2.5 * cm, title=TITULO,
                    author=", ".join(INTEGRANTES), subject=MATERIA)
    doc.multiBuild(construir(), onFirstPage=portada, onLaterPages=pie_pagina)
    print("PDF generado en", SALIDA)


if __name__ == "__main__":
    main()
