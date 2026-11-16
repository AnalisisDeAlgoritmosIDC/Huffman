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
                     leer_texto, describir_caracter, leer_mc)

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
FECHA = "16 de noviembre de 2026"
REPOSITORIO = "https://github.com/AnalisisDeAlgoritmosIDC/Huffman"
URL_APP = "https://huffmanificador.pages.dev"
TITULO = "EL HUFFMANIFICADOR"
SUBTITULO = "Compresor web de texto con el algoritmo de Huffman"

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
                         spaceBefore=6, spaceAfter=10, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName=NOMBRE["Texto-B"], fontSize=12.5, leading=16, textColor=AZUL,
                         spaceBefore=10, spaceAfter=6, keepWithNext=1),
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
    canvas.drawString(2.5 * cm, 1.4 * cm, "%s · %s" % (MATERIA, "El Huffmanificador · Compresor Huffman"))
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
    h.append(Paragraph('Aplicación: <link href="%s" color="#e07a5f">%s</link>' % (URL_APP, URL_APP.replace("https://", "")),
                       E["portada"]))
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
    alice = os.path.join(RAIZ, "libros", "alice_in_wonderland.txt")
    with open(alice, "rb") as f:
        bytes_alice = f.read()
    zlib_alice = len(zlib.compress(bytes_alice, 9))
    info_alice = leer_mc(os.path.join(RAIZ, "pruebas", "salidas", "alice_in_wonderland.mc"))
    info_peq = leer_mc(os.path.join(RAIZ, "pruebas", "salidas", "1_texto_pequeno.mc"))
    info_nuevo = leer_mc(os.path.join(RAIZ, "pruebas", "salidas", "4_archivo_nuevo_persuasion.mc"))
    encabezado_alice = info_alice["inicio_datos"]

    ejemplo = "abracadabra"
    frec_ej = calcular_frecuencias(ejemplo)
    raiz_ej, pasos_ej = construir_arbol(frec_ej)
    cod_ej = generar_codigos(raiz_ej)
    bits_ej = codificar(ejemplo, cod_ej)
    M = NOMBRE["Mono"]

    # ---------------- 1. Introducción
    h.append(p("1. Introducción", "h1"))
    h.append(p(
        "Un algoritmo <b>voraz</b> construye la solución tomando en cada paso la decisión que parece mejor en ese "
        "momento y sin deshacerla después. El <b>algoritmo de Huffman</b> (1952) es el ejemplo clásico: para comprimir "
        "un texto une repetidamente los dos símbolos menos frecuentes y así obtiene un código binario de longitud "
        "variable óptimo, con códigos cortos para los caracteres frecuentes y largos para los raros."))
    h.append(p(
        "<b>El Huffmanificador</b> es una aplicación web pública (<link href=\"%s\" color=\"#e07a5f\">%s</link>) que "
        "implementa Huffman para comprimir y descomprimir textos reales de Project Gutenberg o archivos del usuario. "
        "Genera archivos con un formato propio (<b>.mc</b>), incluye un <b>inspector</b> que examina un archivo "
        "comprimido sin el texto original, mide cuánto espacio se ahorra y verifica que el archivo recuperado sea "
        "idéntico al original. Los algoritmos están escritos en Python y se ejecutan en el navegador." % (URL_APP, URL_APP.replace("https://", ""))))

    # ---------------- 2. Objetivos
    h.append(p("2. Objetivos", "h1"))
    h.append(p(
        "Diseñar, implementar y publicar una aplicación web que use el algoritmo de Huffman y la técnica voraz para "
        "comprimir y descomprimir archivos de texto, permitiendo experimentar con textos reales, analizar la eficiencia "
        "de la compresión y comprender la estructura del archivo comprimido."))
    h.extend(vinetas([
        "Cargar un .txt local o buscar y descargar una obra de Project Gutenberg.",
        "Calcular frecuencias, construir el árbol con la estrategia voraz y generar los códigos.",
        "Generar un archivo comprimido real con formato propio y descomprimirlo sin el .txt original.",
        "Mostrar métricas de compresión y visualizaciones de la tabla, los códigos y el árbol.",
        "Inspeccionar la estructura del archivo comprimido y verificar la integridad del resultado.",
    ]))

    # ---------------- 3. Marco teórico
    h.append(p("3. Marco teórico", "h1"))
    h.append(p("3.1 Algoritmo de Huffman", "h2"))
    h.append(p(
        "Un texto plano usa 8 bits por carácter aunque unos aparezcan mucho más que otros. Un <b>código prefijo</b> "
        "(ningún código es inicio de otro) de longitud variable aprovecha esa diferencia y se puede decodificar sin "
        "separadores. Todo código prefijo es un árbol binario: el camino de la raíz a una hoja (0 = izquierda, "
        "1 = derecha) es el código del carácter. Huffman encuentra el árbol que minimiza el total de bits "
        "B(T) = Σ f(c) · profundidad(c):"))
    h.append(codigo("""
HUFFMAN(C)                         // C = caracteres con su frecuencia f
  Q <- cola de prioridad mínima con los elementos de C
  repetir |C| - 1 veces
      x <- EXTRAER-MIN(Q)          // elección voraz: el menos frecuente
      y <- EXTRAER-MIN(Q)          // y el segundo menos frecuente
      z <- nuevo nodo con hijos x, y y frecuencia x.f + y.f
      INSERTAR(Q, z)
  regresar EXTRAER-MIN(Q)          // raíz del árbol
"""))
    h.append(p(
        "<b>Por qué la elección voraz es óptima:</b> los dos caracteres menos frecuentes pueden colocarse como hermanos "
        "en el nivel más profundo de algún árbol óptimo; al fusionarlos queda un problema del mismo tipo con un símbolo "
        "menos (subestructura óptima). <b>Complejidad:</b> con un heap, construir el árbol es O(n log n) con n = símbolos "
        "distintos; contar, codificar y decodificar son lineales en el tamaño del texto."))
    h.append(p(
        "<b>Entropía de Shannon.</b> H = −Σ p<sub>i</sub> log<sub>2</sub> p<sub>i</sub> es el mínimo de bits por "
        "carácter que puede lograr cualquier código carácter por carácter. Huffman cumple H ≤ L &lt; H + 1, donde L es "
        "su longitud promedio."))
    h.append(p("<b>Ejemplo «abracadabra»</b> (frecuencias a = 5, b = 2, r = 2, c = 1, d = 1):"))
    filas = [["Carácter", "Frecuencia", "Código", "Bits"]]
    for c, f in sorted(frec_ej.items(), key=lambda x: (-x[1], x[0])):
        filas.append([c, f, cod_ej[c], "%d × %d = %d" % (len(cod_ej[c]), f, len(cod_ej[c]) * f)])
    h.append(tabla(filas, [3.5 * cm, 3.5 * cm, 3.5 * cm, 5.5 * cm]))
    h.append(Spacer(1, 6))
    h.append(p("El texto ocupa <b>%d bits</b> en lugar de %d. La construcción del árbol paso a paso y su comprobación "
               "manual están en PRUEBAS.md del repositorio." % (len(bits_ej), len(ejemplo) * 8)))

    # ---------------- 4. Desarrollo
    h.append(p("4. Desarrollo", "h1"))
    h.append(p("4.1 Tecnologías y arquitectura", "h2"))
    h.extend(vinetas([
        "<b>Algoritmos en Python 3</b> (<font face='%s'>huffman/</font>, <font face='%s'>idioma/</font>, "
        "<font face='%s'>mst/</font>): <font face='%s'>heapq</font> para la cola de prioridad, "
        "<font face='%s'>hashlib</font> para SHA-256 y <font face='%s'>struct</font> para el formato binario." % ((M,) * 6),
        "<b>Pyodide 0.26</b> ejecuta ese mismo código de Python en el navegador; "
        "<font face='%s'>web/puente.py</font> expone las funciones que llama la interfaz." % M,
        "<b>Interfaz</b> en HTML, CSS y JavaScript (módulos ES), sin frameworks.",
        "<b>Cloudflare Pages</b> (gratuito) publica la página desde GitHub; una <i>Pages Function</i> "
        "(<font face='%s'>functions/api/[[ruta]].js</font>) busca y descarga libros de gutenberg.org, porque "
        "Gutenberg no permite que otras páginas lean sus archivos desde el navegador (CORS)." % M,
        "<b>GitHub</b> para el código y el historial; <b>GitHub Projects</b> para el tablero de tareas.",
    ]))
    h.append(p("4.2 Formato propio .mc", "h2"))
    h.append(p("El archivo no guarda el texto, solo lo necesario para reconstruirlo. Enteros en big-endian:"))
    h.append(tabla([
        ["Offset", "Bytes", "Campo"],
        ["0", "3 + 1", "Firma «HMC» y versión del formato (2)"],
        ["4", "8", "Tamaño del archivo original en bytes"],
        ["12", "8", "Número de caracteres del texto"],
        ["20", "8 + 1", "Total de bits válidos y bits de relleno del último byte"],
        ["29", "8", "Fecha de creación"],
        ["37", "32", "SHA-256 del archivo original (integridad)"],
        ["69", "1 + n, 2 + m", "Codificación del texto y nombre del archivo original"],
        ["…", "4 + K × (1 + n + 4)", "Tabla de frecuencias: K símbolos con su frecuencia"],
        ["…", "⌈bits / 8⌉", "Datos: códigos de Huffman empaquetados en bytes"],
    ], [2.2 * cm, 3.6 * cm, 10.7 * cm]))
    h.append(Spacer(1, 6))
    h.append(p(
        "Se guarda la <b>tabla de frecuencias</b> y no los códigos porque es compacta y la construcción del árbol es "
        "determinista (desempate por frecuencia, carácter y orden de inserción): con la misma tabla se obtienen los "
        "mismos códigos. En <i>Alice</i>, encabezado y tabla ocupan %d bytes de %s. La especificación completa, con un "
        "ejemplo byte por byte, está en <font face='%s'>FORMATO.md</font>." % (
            encabezado_alice, miles(info_alice["tamano_comprimido"]), M)))
    h.append(p("4.3 Flujo de la aplicación e Inspector", "h2"))
    h.append(p(
        "La página guía el flujo BUSCAR / SUBIR → ANALIZAR → CONSTRUIR HUFFMAN → COMPRIMIR → INSPECCIONAR → "
        "DESCOMPRIMIR con una barra de pasos. Tras comprimir muestra el tamaño original y el comprimido (bytes y KB/MB), "
        "los bytes ahorrados, el porcentaje de reducción, la razón de compresión y el número de símbolos."))
    h.append(p(
        "El <b>Inspector</b> abre un .mc sin el texto original: lee el encabezado (versión, tamaños, bits, relleno, "
        "fecha, hash, nombre), reconstruye la tabla, los códigos y el árbol, dibuja un mapa de las secciones del "
        "archivo, un volcado hexadecimal coloreado por sección y los primeros bits de los datos. Solo al presionar "
        "<b>DESCOMPRIMIR</b> recupera el texto, compara su tamaño y su SHA-256 con los guardados y permite descargarlo."))
    h.append(p(
        "Para entender el algoritmo, el árbol se puede ver en cuatro formas (jerárquica, radial, explorador y "
        "construcción paso a paso con la cola de prioridad animada), y una sección de ahorro interactivo muestra la "
        "curva de bits acumulados y los bits de cada carácter. La página también detecta el idioma del texto y "
        "tiene una sección de árbol de expansión mínima (Kruskal y Prim)."))

    # ---------------- 5. Pruebas y resultados
    h.append(PageBreak())
    h.append(p("5. Pruebas y resultados", "h1"))
    h.append(p("5.1 Pruebas mínimas", "h2"))
    h.append(p("Cada prueba recorre original.txt → archivo.mc → recuperado.txt (script "
               "<font face='%s'>pruebas/ejecutar_pruebas.py</font>):" % M))

    def fila(nombre, info):
        o, c = info["tamano_original"], info["tamano_comprimido"]
        return [nombre, "%s B" % miles(o), "%s B" % miles(c), "%s B" % miles(o - c), "%.2f %%" % ((1 - c / o) * 100),
                info["simbolos"], "✔"]
    h.append(tabla([
        ["Prueba", "Original", ".mc", "Ahorrado", "Reducción", "Símb.", "Íntegro"],
        fila("1. Texto pequeño (abracadabra)", info_peq),
        fila("2. Libro Gutenberg (Alice)", info_alice),
        fila("4. Archivo nuevo (Persuasion)", info_nuevo),
    ], [5.2 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 1.9 * cm, 1.3 * cm, 1.4 * cm]))
    h.append(Spacer(1, 6))
    h.extend(vinetas([
        "<b>1. Texto pequeño:</b> las frecuencias, el árbol y los códigos calculados a mano coinciden con los del "
        "programa (23 bits). El .mc es más grande que el original porque el encabezado pesa más que el texto.",
        "<b>2. Libro de Gutenberg:</b> <i>Alice</i> se reduce 42.29 %; el árbol tiene 73 hojas.",
        "<b>3. Integridad:</b> en los tres casos el archivo recuperado es idéntico byte a byte y con el mismo "
        "SHA-256. Al alterar un solo bit de los datos de un .mc, la verificación lo detecta.",
        "<b>4. Archivo no usado en el desarrollo:</b> <i>Persuasion</i> (Jane Austen) se comprime y recupera "
        "correctamente. En la revisión se puede repetir con cualquier .txt.",
        "Además hay 18 pruebas unitarias (casos límite, formato, versión anterior, archivos inválidos, idioma y MST).",
    ]))
    if libros:
        h.append(p("5.2 Comparación con varios libros", "h2"))
        filas = [["Libro", "Original", ".mc", "Reducción", "Bits/car.", "Entropía"]]
        for f in libros:
            filas.append([f["libro"].replace("_", " "), "%.1f KB" % (int(f["original_B"]) / 1024),
                          "%.1f KB" % (int(f["huf_B"]) / 1024), "%s %%" % f["ahorro_%"], f["bits_promedio"], f["entropia"]])
        h.append(tabla(filas, [4.4 * cm, 2.4 * cm, 2.4 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm]))
        h.append(Spacer(1, 6))
    h.append(p("5.3 Capturas de la aplicación", "h2"))
    h += figura("01_huffman_flujo_libro_y_metricas.png",
                "Figura 1. Barra de flujo, búsqueda en Project Gutenberg y métricas de compresión de Alice.")
    h += figura("03_huffman_arbol_jerarquico.png",
                "Figura 2. Árbol de Huffman; al seleccionar «e» (código 000) se resalta su camino.")
    h += figura("06_huffman_construccion_paso_a_paso.png",
                "Figura 3. Construcción voraz paso a paso: cola de prioridad y los dos nodos que se unen.")
    h += figura("12_inspector_estructura.png",
                "Figura 4. Inspector: metadatos leídos del encabezado del .mc y mapa de sus secciones.", ancho=15 * cm)
    h += figura("13_inspector_bytes_y_bits.png",
                "Figura 5. Inspector: volcado hexadecimal coloreado por sección y bits codificados.", ancho=15 * cm)
    h += figura("16_inspector_descomprimido_verificado.png",
                "Figura 6. Descompresión desde el Inspector con verificación de tamaño y SHA-256.")
    h += figura("07_huffman_ahorro_interactivo.png",
                "Figura 7. Ahorro interactivo: total, curva de bits acumulados y vista carácter por carácter.",
                ancho=12 * cm)

    # ---------------- 6. Análisis
    h.append(p("6. Análisis", "h1"))
    h.append(p(
        "En los cinco textos la reducción fue de 42 a 44 %%: Huffman baja de 8 a unos 4.6 bits por carácter y queda a "
        "menos de 0.05 bits de la entropía, así que el código es prácticamente óptimo para una codificación carácter "
        "por carácter. Construir el árbol tarda menos de un milisegundo porque depende solo de los ≈ 75 símbolos "
        "distintos; contar, codificar y decodificar crecen de forma lineal con el texto. Como referencia, ZIP "
        "(DEFLATE) reduce <i>Alice</i> a %s bytes (%.1f %%), porque además aprovecha palabras repetidas; Huffman "
        "solo ve caracteres aislados." % (miles(zlib_alice), (1 - zlib_alice / len(bytes_alice)) * 100)))

    # ---------------- 7. Uso de IA
    h.append(p("7. Uso de inteligencia artificial", "h1"))
    h.append(p(
        "Se usó Claude (Anthropic) para proponer la estructura del proyecto, generar código inicial, adaptar el diseño "
        "visual, depurar el deployment en Cloudflare y redactar documentación. Los resultados se validaron con las "
        "pruebas unitarias, la comprobación manual de «abracadabra», la verificación byte a byte y SHA-256 de los "
        "archivos recuperados y pruebas en la página publicada. Cada integrante revisó y puede explicar su parte del código."))

    # ---------------- 8. Limitaciones
    h.append(p("8. Limitaciones", "h1"))
    h.extend(vinetas([
        "En archivos muy pequeños el .mc puede ser más grande que el original (encabezado ≈ 100 B más la tabla).",
        "Huffman por carácter no aprovecha repeticiones de palabras; compresores como ZIP logran más.",
        "Solo se aceptan textos (.txt en UTF-8 o Latin-1).",
        "Todo corre en el navegador: libros de varios MB tardan algunos segundos y se necesita internet para "
        "cargar Pyodide y para el buscador de Gutenberg.",
    ]))

    # ---------------- 9. Conclusiones
    h.append(p("9. Conclusiones", "h1"))
    h.append(p(
        "Se implementó y publicó un compresor web completo basado en Huffman: transforma las frecuencias en un árbol "
        "mediante la elección voraz, el árbol en códigos y los códigos en un archivo binario propio que se puede "
        "inspeccionar y reconstruir sin el texto original. Las pruebas con libros reales mostraron una reducción "
        "cercana al 42 %, muy próxima al límite de la entropía, y todos los archivos recuperados fueron idénticos "
        "al original, lo que se verifica con SHA-256 guardado en el propio formato."))
    h.append(p(
        "Diseñar el formato .mc y el Inspector obligó a entender qué información es realmente necesaria para "
        "descomprimir (la tabla de frecuencias, los bits válidos y el relleno) y cómo garantizar la integridad. "
        "Como mejora futura se podría aplicar Huffman sobre palabras o combinarlo con LZ77 para acercarse a ZIP."))

    # ---------------- 10. Referencias
    h.append(p("10. Referencias", "h1"))
    for r in [
        "Cormen, T. H., Leiserson, C. E., Rivest, R. L., &amp; Stein, C. (2009). <i>Introduction to "
        "algorithms</i> (3.ª ed.). MIT Press. (Cap. 16: Greedy Algorithms).",
        "Huffman, D. A. (1952). A method for the construction of minimum-redundancy codes. <i>Proceedings of "
        "the IRE, 40</i>(9), 1098–1101. https://doi.org/10.1109/JRPROC.1952.273898",
        "Shannon, C. E. (1948). A mathematical theory of communication. <i>Bell System Technical Journal, "
        "27</i>(3), 379–423.",
        "Kruskal, J. B. (1956). On the shortest spanning subtree of a graph and the traveling salesman "
        "problem. <i>Proceedings of the American Mathematical Society, 7</i>(1), 48–50.",
        "Prim, R. C. (1957). Shortest connection networks and some generalizations. <i>Bell System Technical "
        "Journal, 36</i>(6), 1389–1401.",
        "Carroll, L. (1865). <i>Alice's adventures in Wonderland</i>. Project Gutenberg. https://www.gutenberg.org/ebooks/11",
        "Austen, J. (1817). <i>Persuasion</i>. Project Gutenberg. https://www.gutenberg.org/ebooks/105",
        "Pyodide contributors. (2024). <i>Pyodide</i> (versión 0.26). https://pyodide.org",
        "Cloudflare. (2025). <i>Cloudflare Pages documentation</i>. https://developers.cloudflare.com/pages/",
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
