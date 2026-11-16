# EL HUFFMANIFICADOR

Aplicación web que comprime y descomprime textos con el **algoritmo de Huffman** (técnica voraz), con un formato
de archivo propio (**`.mc`**), un **inspector** de archivos comprimidos, integración con **Project Gutenberg** y
visualizaciones del algoritmo. Incluye además detección de idioma y el árbol de expansión mínima (Kruskal y Prim).

- **Aplicación publicada:** https://huffmanificador.pages.dev
- **Repositorio:** https://github.com/AnalisisDeAlgoritmosIDC/Huffman
- **GitHub Projects:** *(agregar aquí la URL del tablero)*
- **Materia:** Análisis de Algoritmos · CUCEI, Universidad de Guadalajara · 2026B

## Integrantes

| Integrante | Responsabilidades principales |
|---|---|
| Carlos Adrian Ramirez Gutiérrez | Interfaz y diseño, visualizaciones, Inspector, reporte, documentación |
| Isaac Saldivar Zaldivar | Algoritmo de Huffman, formato .mc, descompresor e integridad, detección de idioma, Python en el navegador |
| Daniel Padilla Echeverria | Integración con Gutenberg, deployment, árbol de expansión mínima, pruebas y análisis |

## Flujo de la aplicación

`BUSCAR LIBRO / SUBIR .TXT → ANALIZAR → CONSTRUIR HUFFMAN → COMPRIMIR → INSPECCIONAR → DESCOMPRIMIR Y VERIFICAR`

La página muestra este flujo como una barra de pasos que se va completando.

1. **Entrada:** buscar una obra en Project Gutenberg por título, autor o palabras clave (con filtro de idioma), o
   arrastrar un `.txt` propio.
2. **Analizar y construir Huffman:** frecuencias, árbol, códigos e idioma del texto.
3. **Comprimir:** genera un archivo `.mc` real que se puede descargar.
4. **Inspeccionar:** el Inspector abre un `.mc` **sin el .txt original** y muestra su estructura: metadatos, mapa de
   bytes, volcado hexadecimal, bits, tabla de frecuencias, códigos y árbol reconstruidos.
5. **Descomprimir y verificar:** recupera el texto, comprueba tamaño y SHA-256 contra lo guardado en el `.mc` y
   permite descargar el `.txt` recuperado.

## Descripción del algoritmo

1. **Frecuencias:** se cuenta cuántas veces aparece cada carácter (`collections.Counter`).
2. **Árbol (técnica voraz):** cada carácter es una hoja en una cola de prioridad (`heapq`). Mientras quede más de un
   nodo se extraen los **dos de menor frecuencia**, se unen en un nodo padre cuya frecuencia es la suma y el padre
   vuelve a la cola. El último nodo es la raíz. Construirlo cuesta **O(n log n)** con *n* = símbolos distintos.
3. **Códigos:** se recorre el árbol; izquierda agrega `0` y derecha `1`. Ningún código es prefijo de otro, por eso
   se puede decodificar sin separadores.
4. **Codificación:** cada carácter se sustituye por su código y la cadena de bits se empaqueta en bytes.
5. **Decodificación:** se recorre el árbol bit por bit desde la raíz; al llegar a una hoja se escribe su carácter.

La elección voraz es óptima: los dos símbolos menos frecuentes pueden ir como hermanos en el nivel más profundo de
algún árbol óptimo, y al fusionarlos el problema se reduce a uno más pequeño del mismo tipo. En los libros probados,
la longitud promedio de código queda a menos de 0.05 bits de la **entropía de Shannon** (el mínimo teórico).

## Formato propio `.mc`

Documentado en **[FORMATO.md](FORMATO.md)**. Resumen:

| Sección | Contenido |
|---|---|
| Encabezado | Firma `HMC` + versión (2), tamaño original, número de caracteres, bits válidos, bits de relleno, fecha, **SHA-256 del original**, codificación y nombre del archivo original |
| Tabla de frecuencias | K símbolos con su frecuencia, para reconstruir el árbol |
| Datos | Bits de Huffman empaquetados en bytes |

El `.mc` no contiene el texto original; se descomprime sin necesitar el `.txt`.

## Resultados de compresión

| Libro (Project Gutenberg) | Original | Comprimido (.mc) | Ahorrado | Reducción | Símbolos |
|---|---|---|---|---|---|
| Alice in Wonderland | 144,395 B (141.01 KB) | 83,332 B (81.38 KB) | 61,063 B | 42.29 % | 73 |
| Hamlet | 162,881 B (159.06 KB) | 94,401 B (92.19 KB) | 68,480 B | 42.04 % | 67 |
| Moby Dick | 1,242,990 B (1.19 MB) | 711,928 B (695.24 KB) | 531,062 B | 42.72 % | 82 |
| King James Bible | 4,332,554 B (4.13 MB) | 2,480,978 B (2.37 MB) | 1,851,576 B | 42.74 % | 75 |
| Persuasion (archivo nuevo) | 466,292 B (455.36 KB) | 260,672 B (254.56 KB) | 205,620 B | 44.10 % | 78 |

En todos los casos el archivo recuperado es idéntico al original (byte a byte y SHA-256). Detalle y gráficas en
[`analisis/resultados/`](analisis/resultados/) y [`pruebas/RESULTADOS.md`](pruebas/RESULTADOS.md).

## Pruebas y evidencias

Ver **[PRUEBAS.md](PRUEBAS.md)**: texto pequeño comprobado a mano, libro de Gutenberg, integridad (incluida la
detección de un `.mc` alterado) y un archivo no utilizado durante el desarrollo. Capturas de la aplicación en
[`capturas/`](capturas/).

```bash
python pruebas/ejecutar_pruebas.py               # pruebas mínimas → pruebas/RESULTADOS.md
python -m unittest discover -s tests -v          # 18 pruebas unitarias
```

## Tecnologías utilizadas

| Parte | Tecnología |
|---|---|
| Algoritmos (Huffman, formato .mc, integridad, idioma, Kruskal, Prim) | **Python 3** (`heapq`, `collections`, `hashlib`, `struct`) |
| Ejecutar Python en el navegador | **Pyodide 0.26** (CPython compilado a WebAssembly) |
| Interfaz | HTML, CSS y JavaScript (módulos ES), sin frameworks |
| Búsqueda y descarga de libros | Cloudflare Pages Functions (`functions/api/[[ruta]].js`) con la lógica de `worker/index.js`; consulta gutenberg.org (Gutendex como respaldo) |
| Hosting | Cloudflare Pages (gratuito), conectado a GitHub |
| Pruebas | `unittest` |
| Análisis y reporte | matplotlib, reportlab |

Todos los servicios usados son gratuitos.

## Instrucciones de ejecución

**Usar la aplicación:** abrir https://huffmanificador.pages.dev (necesita internet para cargar Pyodide la primera
vez; tarda unos segundos hasta que arriba dice **PYTHON LISTO**).

**Ejecutarla en local** (necesita Node.js):

```bash
git clone https://github.com/AnalisisDeAlgoritmosIDC/Huffman.git
cd Huffman
npx wrangler dev          # abre http://localhost:8787 con el buscador funcionando
```

Abrir `index.html` con doble clic **no funciona**: el navegador bloquea los módulos y los archivos de Python (la
página muestra un aviso explicándolo).

**Publicar en Cloudflare Pages:** Workers & Pages → Create → Pages → *Import an existing Git repository* →
`AnalisisDeAlgoritmosIDC/Huffman`; Framework preset **None**, Build command vacío, Build output directory vacío
(raíz). Cada `git push` publica de nuevo. (Alternativa en Workers: `npx wrangler deploy`, usa `wrangler.jsonc`.)

**Usar los algoritmos desde Python** (sin la página):

```python
from huffman import *
texto, cod = leer_texto("libros/alice_in_wonderland.txt")
frec = calcular_frecuencias(texto)
raiz, pasos = construir_arbol(frec)
codigos = generar_codigos(raiz)
bits = codificar(texto, codigos)
guardar_comprimido("alice.mc", frec, bits, cod, open("libros/alice_in_wonderland.txt", "rb").read(), "alice.txt")
print(leer_mc("alice.mc")["tamano_original"])
texto2, verificacion = descomprimir_y_verificar("alice.mc", "alice_recuperado.txt")
```

## Estructura del repositorio

```
index.html                  página
web/                        interfaz (JavaScript) + puente.py (Python que llama la página)
  python.js                 carga Pyodide y los módulos .py
  puente.py                 analizar, comprimir, inspeccionar, descomprimir, grafos
  huffman_ui.js             sección de Huffman          inspector.js   Inspector .mc
  arbol.js, arbol_radial.js, construccion.js            vistas del árbol
  ahorro.js, idioma_ui.js, mst_ui.js, buscador.js, flujo.js, app.js, styles.css
huffman/                    algoritmo de Huffman y formato .mc (Python)
idioma/                     detección de idioma (Python)
mst/                        Kruskal, Prim y grafos (Python)
functions/api/[[ruta]].js   servidor del buscador en Cloudflare Pages
worker/index.js             misma lógica como Cloudflare Worker
tests/                      pruebas unitarias
pruebas/                    pruebas mínimas documentadas y evidencias
analisis/                   medición de rendimiento y gráficas
libros/                     libros de Project Gutenberg usados en las pruebas
capturas/                   capturas de la aplicación
reporte/                    reporte técnico en PDF y script que lo genera
FORMATO.md · PRUEBAS.md · BACKLOG.md
```

## Uso de inteligencia artificial

Se usó **Claude** (Anthropic) como asistente para:

- proponer la estructura del proyecto y generar código inicial de los módulos de Python y de la interfaz;
- adaptar el diseño visual (tema morado tinto) a partir de una plantilla del equipo;
- depurar errores de deployment (archivos faltantes en Cloudflare, servidor del buscador en Pages);
- redactar documentación, el plan de commits y el reporte.

**Cómo se validó:**

- 18 pruebas unitarias y las pruebas mínimas de `pruebas/ejecutar_pruebas.py`;
- comprobación manual del ejemplo «abracadabra» (frecuencias, árbol, códigos y bits);
- verificación byte a byte y con SHA-256 de todos los archivos recuperados;
- pruebas en la página publicada con libros de Gutenberg y un archivo nuevo.

Cada integrante revisó y es responsable de explicar el código de su parte.

## Limitaciones conocidas

- **Archivos muy pequeños:** el encabezado (≈ 100 bytes) y la tabla de frecuencias pueden hacer que el `.mc` sea
  más grande que el original (por ejemplo, «abracadabra»: 11 B → 133 B).
- **Huffman carácter por carácter:** no aprovecha palabras o frases repetidas. En *Alice*, ZIP (DEFLATE) logra
  ≈ 64 % de reducción contra ≈ 42 % de Huffman.
- **Solo texto:** se aceptan `.txt` en UTF-8 o Latin-1; no está pensado para archivos binarios.
- **Rendimiento en el navegador:** todo corre en la computadora del usuario. Libros de varios MB tardan algunos
  segundos y la página no responde mientras decodifica.
- **Requiere internet** para descargar Pyodide (≈ 10 MB la primera vez) y para el buscador.
- **Buscador:** depende de que gutenberg.org (o Gutendex) responda, y solo usa obras con versión en texto plano.
- **Frecuencias de 4 bytes:** cada símbolo puede aparecer hasta ≈ 4,290 millones de veces.
- **Detección de idioma:** reconoce 8 idiomas; con textos muy cortos puede no identificarlo.

## Otros

- **Árbol de expansión mínima:** sección aparte con Kruskal (Union-Find) y Prim (heap), paso a paso.
- **Libros incluidos** (dominio público, Project Gutenberg): *Alice's Adventures in Wonderland*, *Hamlet*,
  *Moby Dick*, *The King James Bible*; *Persuasion* en `pruebas/`.
