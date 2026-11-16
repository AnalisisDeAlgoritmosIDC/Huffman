# EL HUFFMANIFICADOR

Página web de algoritmos voraces: compresión de libros de Project Gutenberg con **Huffman** (archivos `.mc`),
**detección de idioma** y **Árbol de Expansión Mínima** (Kruskal y Prim).

Repositorio: https://github.com/AnalisisDeAlgoritmosIDC/Huffman

**Equipo:** Carlos Adrian Ramirez Gutiérrez · Isaac Saldivar Zaldivar · Daniel Padilla Echeverria

## Cómo funciona

Los algoritmos están escritos en **Python** (`huffman/`, `mst/`, `idioma/`) y se ejecutan **dentro del
navegador** con [Pyodide](https://pyodide.org) (Python compilado a WebAssembly). JavaScript solo dibuja la
interfaz: `web/puente.py` expone las funciones de Python que llama la página y regresa los resultados en JSON.

El **buscador de libros** busca directamente en `gutenberg.org/ebooks/search` (con filtro de idioma) y descarga el
`.txt` del libro elegido. Como Gutenberg no permite que una página de otro dominio lea sus respuestas (CORS), las
peticiones pasan por un **Cloudflare Worker** (`worker/index.js`). Si la búsqueda directa falla, usa como
respaldo la API Gutendex, que expone el mismo catálogo de Gutenberg.

## Qué hace la página

**Huffman**
1. Buscar un libro en Project Gutenberg (o arrastrar un `.txt` propio).
2. Contar frecuencias, construir el árbol con la técnica voraz y generar los códigos.
3. **Codificar** a `.mc`, **decodificar** de regreso y verificar que el texto sea idéntico byte por byte.
4. Comparar tamaños: original vs comprimido, ahorro, bits promedio, entropía de Shannon y eficiencia.

Además:
- **4 vistas del árbol:** jerárquica, radial (cada círculo = 1 bit más de código), explorador desplegable y
  construcción paso a paso (la cola de prioridad animada, resaltando los dos nodos que se unen).
- **Ahorro interactivo:** curva de bits acumulados (original vs Huffman) que se recorre con el mouse, vista
  carácter por carácter con sus bits, qué caracteres ahorran o cuestan más y una calculadora.
- **Detección de idioma** (`idioma/detector.py`): cuenta las palabras vacías de 8 idiomas (pesadas según qué
  tan exclusivas son) y las letras características; ignora el encabezado en inglés de Gutenberg.
- Subir un `.mc` para decodificarlo.

**Árbol de expansión mínima**
- Genera un grafo conexo aleatorio (número de nodos, densidad y semilla configurables).
- Ejecuta **Kruskal** (ordena aristas y usa Union-Find para evitar ciclos) o **Prim** (crece desde un nodo
  inicial con un heap), completo, paso a paso o animado, con una bitácora de cada decisión.
- Al terminar compara el peso con el del otro algoritmo (siempre coinciden).

## Estructura

```
index.html              página
web/
  styles.css            estilos (tema morado tinto)
  app.js                navegación e inicio
  python.js             carga Pyodide y los módulos .py
  puente.py             funciones de Python que llama la página
  buscador.js           buscador de Gutenberg y carga de archivos
  huffman_ui.js         sección de Huffman
  arbol.js              vistas del árbol: jerárquica y explorador
  arbol_radial.js       vista radial del árbol
  construccion.js       construcción paso a paso (cola de prioridad animada)
  ahorro.js             ahorro interactivo
  idioma_ui.js          resultado de la detección de idioma
  mst_ui.js             sección de Kruskal / Prim
huffman/
  frecuencias.py        lectura del .txt y conteo de frecuencias
  arbol.py              nodo y construcción voraz del árbol (heap)
  codigos.py            recorrido del árbol -> códigos binarios
  codificador.py        codificar / decodificar y formato de archivo .mc
  estadisticas.py       longitud promedio, entropía, comparación de tamaños
mst/
  grafo.py              grafo ponderado y generador aleatorio conexo
  kruskal.py            Kruskal + Union-Find
  prim.py               Prim con cola de prioridad
idioma/
  detector.py           detección de idioma
worker/index.js         Worker de Cloudflare: /api/buscar y /api/libro/<id>
functions/api/[[ruta]].js  lo mismo para Cloudflare Pages
wrangler.jsonc          configuración de Cloudflare
.assetsignore           carpetas que no se publican en la página
tests/                  pruebas unitarias (unittest)
analisis/               medición de rendimiento y gráficas
libros/                 libros de Project Gutenberg usados en las pruebas
salidas/                ejemplo de archivo .mc y su decodificación
capturas/               capturas del funcionamiento
reporte/                reporte en PDF y script que lo genera
```

## Publicar en Cloudflare

**Opción A · Cloudflare Pages conectado a GitHub (la que usamos: huffmanificador.pages.dev)**
1. **Workers & Pages → Create → Pages → Import an existing Git repository** y elegir
   `AnalisisDeAlgoritmosIDC/Huffman`.
2. *Framework preset*: **None** · *Build command*: vacío · *Build output directory*: `/`
3. **Save and Deploy**. Cada `git push` vuelve a publicar la página.

El buscador funciona gracias a `functions/api/[[ruta]].js`, que Pages ejecuta como servidor y que reutiliza
la lógica de `worker/index.js`.

**Opción B · Cloudflare Workers**
- Desde GitHub: **Workers & Pages → Create → Import a repository**, *build command* vacío y *deploy command*
  `npx wrangler deploy`.
- Desde tu compu (necesita Node.js): `npx wrangler login` y luego `npx wrangler deploy`.

Para probarla en local: `npx wrangler dev` y abrir http://localhost:8787. Si abres `index.html` con doble clic
no funciona: el navegador bloquea el código de la página (la propia página muestra un aviso).

> No usen la subida manual de archivos ("Upload your static files" / arrastrar la carpeta): no publica el
> servidor del buscador y es fácil que se queden archivos fuera.

## Pruebas y análisis (opcional, con Python instalado)

```bash
python -m unittest discover -s tests -v          # 14 pruebas
pip install -r requirements.txt
python analisis/medir_rendimiento.py             # tablas y gráficas de rendimiento
python reporte/generar_reporte.py                # regenera el PDF
```

## Formato del archivo `.mc`

| Campo | Tamaño |
|---|---|
| Firma `HMC1` | 4 bytes |
| Largo + nombre de la codificación del texto | 1 + n bytes |
| Número de caracteres distintos K | 4 bytes |
| K × (largo UTF-8, carácter, frecuencia) | K × (1 + 1..4 + 4) bytes |
| Bits de relleno del último byte | 1 byte |
| Datos codificados | ⌈bits / 8⌉ bytes |

## Libros utilizados

Textos de dominio público de [Project Gutenberg](https://www.gutenberg.org/):
*Alice's Adventures in Wonderland* (Lewis Carroll), *Hamlet* (Shakespeare), *Moby Dick* (Herman Melville) y
*The King James Bible*. En la página se puede buscar y usar cualquier otro libro de Gutenberg.
