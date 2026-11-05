# EL HUFFMANIFICADOR

Algoritmos voraces: compresión de texto con Huffman (archivos `.mc`) y Árbol de Expansión Mínima.

Repositorio: https://github.com/AnalisisDeAlgoritmosIDC/Huffman

**Equipo:** Carlos Adrian Ramirez Gutiérrez · Isaac Saldivar Zaldivar · Daniel Padilla Echeverria

Proyecto de Análisis de Algoritmos. Implementa en Python, con interfaz gráfica (tkinter):

1. **Compresión de Huffman**: lee un `.txt`, calcula la frecuencia de cada carácter, construye el
   árbol de Huffman con la técnica voraz, genera los códigos binarios, codifica el archivo a `.mc`,
   lo decodifica de regreso y compara tamaños.
2. **Árbol de expansión mínima**: Kruskal y Prim sobre grafos aleatorios, con animación paso a paso.

## Instalación y uso

Requiere **Python 3.8 o superior**. La interfaz usa solo la biblioteca estándar (tkinter ya viene
con Python en Windows y macOS; en Linux puede ser necesario `sudo apt install python3-tk`).

```bash
python main.py
```

Opcional (solo para generar las gráficas de rendimiento):

```bash
pip install -r requirements.txt
python analisis/medir_rendimiento.py
```

Pruebas unitarias:

```bash
python -m unittest discover -s tests -v
```

## Estructura

```
main.py                     Punto de entrada (versión de escritorio)
huffman/
  frecuencias.py            Lectura del .txt y conteo de frecuencias
  arbol.py                  Nodo y construcción voraz del árbol (heap)
  codigos.py                Recorrido del árbol -> códigos binarios
  codificador.py            Codificar / decodificar y formato de archivo .mc
  estadisticas.py           Longitud promedio, entropía, comparación de tamaños
mst/
  grafo.py                  Grafo ponderado y generador aleatorio conexo
  kruskal.py                Kruskal + Union-Find
  prim.py                   Prim con cola de prioridad
gui/
  estilos.py                Colores y estilo ttk
  app.py                    Ventana principal con pestañas
  tab_huffman.py            Pestaña de Huffman
  vista_arbol.py            Dibujo del árbol de Huffman (zoom, scroll, resaltado)
  tab_mst.py                Pestaña de Kruskal / Prim con animación
tests/                      Pruebas unitarias (unittest)
analisis/                   Script de medición de rendimiento y resultados
libros/                     Libros de Project Gutenberg usados en las pruebas
capturas/                   Capturas del funcionamiento
reporte/                    Reporte en PDF y script que lo genera
```

## Versión web (página publicada)

La misma lógica de Python corre en el navegador con [Pyodide](https://pyodide.org) (Python compilado a
WebAssembly). JavaScript solo dibuja la interfaz; los algoritmos son los archivos de `huffman/` y `mst/`.

Además de todo lo de la versión de escritorio, la página tiene:

- **4 vistas del árbol:** jerárquica, radial (cada círculo = 1 bit más de código), explorador desplegable y
  construcción paso a paso (la cola de prioridad animada, resaltando los dos nodos que se unen).
- **Ahorro interactivo:** curva de bits acumulados (original vs Huffman) que se recorre con el mouse, vista
  carácter por carácter con sus bits, qué caracteres ahorran o cuestan más y una calculadora.
- **Detección de idioma** (`idioma/detector.py`): cuenta las palabras vacías de 8 idiomas (pesadas según qué
  tan exclusivas son) y las letras características; ignora el encabezado en inglés de Gutenberg.

La página tiene un **buscador de libros de Project Gutenberg**: busca directamente en
`gutenberg.org/ebooks/search` (con filtro de idioma) y descarga el `.txt` del libro elegido. Como Gutenberg no
permite que una página de otro dominio lea sus respuestas (CORS), las peticiones pasan por un
**Cloudflare Worker** (`worker/index.js`). Si la búsqueda directa falla, usa como respaldo la API Gutendex,
que expone el mismo catálogo de Gutenberg.

```
index.html              página
web/
  styles.css            estilos
  app.js                pestañas e inicio
  python.js             carga Pyodide y los módulos .py
  puente.py             funciones de Python que llama la página (usa huffman/ y mst/)
  buscador.js           buscador de Gutenberg y carga de archivos
  huffman_ui.js         pestaña de Huffman
  arbol.js              vistas del árbol: jerárquica y explorador
  arbol_radial.js       vista radial del árbol
  construccion.js       construcción paso a paso (cola de prioridad animada)
  ahorro.js             ahorro interactivo (curva, carácter por carácter, calculadora)
  idioma_ui.js          resultado de la detección de idioma
  mst_ui.js             pestaña de Kruskal / Prim
idioma/
  detector.py           detección de idioma (Python)
worker/index.js         Worker: /api/buscar y /api/libro/<id>
wrangler.jsonc          configuración de Cloudflare
.assetsignore           carpetas que no se publican
```

### Publicar en Cloudflare

1. Subir el repo a GitHub.
2. En Cloudflare: **Workers & Pages → Create → Import a repository** y elegir el repo.
3. Dejar el *build command* vacío; el *deploy command* es `npx wrangler deploy` (Cloudflare lee
   `wrangler.jsonc` solo).
4. Cada `git push` vuelve a publicar la página.

Para probarla en tu compu: `npx wrangler dev` y abrir http://localhost:8787. Si abres `index.html` con doble
clic no funciona, porque el navegador no deja cargar los `.py` desde un archivo local.

## Pestaña Huffman

1. **Abrir archivo .txt**: calcula frecuencias, construye el árbol y muestra la tabla
   carácter / frecuencia / probabilidad / código / bits. Al seleccionar un carácter se resalta su
   camino en el árbol.
2. **Codificar y guardar .mc**: genera la cadena de bits, la empaqueta en bytes y guarda el archivo
   comprimido (incluye la tabla de frecuencias para poder reconstruir el árbol).
3. **Decodificar .mc → .txt**: lee el `.mc`, reconstruye el árbol, recupera el texto y verifica que
   sea idéntico byte por byte al original.

La pestaña *Resultados de compresión* muestra tamaño original vs comprimido, razón de compresión,
bits promedio por carácter, entropía de Shannon, eficiencia del código y tiempos.

### Formato del archivo `.mc`

| Campo | Tamaño |
|---|---|
| Firma `HMC1` | 4 bytes |
| Largo + nombre de la codificación del texto | 1 + n bytes |
| Número de caracteres distintos K | 4 bytes |
| K × (largo UTF-8, carácter, frecuencia) | K × (1 + 1..4 + 4) bytes |
| Bits de relleno del último byte | 1 byte |
| Datos codificados | ⌈bits / 8⌉ bytes |

## Pestaña Árbol de expansión mínima

- Genera un grafo conexo aleatorio (número de nodos, densidad y semilla configurables).
- Ejecuta **Kruskal** (ordena aristas y usa Union-Find para evitar ciclos) o **Prim**
  (crece desde un nodo inicial con un heap).
- *Siguiente paso* / *Animar* muestran cada decisión voraz: aristas aceptadas en verde,
  rechazadas en rojo punteado. Al terminar compara el peso con el otro algoritmo.

## Libros utilizados

Textos de dominio público de [Project Gutenberg](https://www.gutenberg.org/):
*Alice's Adventures in Wonderland* (Lewis Carroll), *Hamlet* (Shakespeare), *Moby Dick*
(Herman Melville) y *The King James Bible*. Cualquier otro `.txt` de Gutenberg funciona igual.
