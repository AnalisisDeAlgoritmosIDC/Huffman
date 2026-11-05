# Algoritmos voraces: Huffman y Árbol de Expansión Mínima

Proyecto de Análisis de Algoritmos. Implementa en Python, con interfaz gráfica (tkinter):

1. **Compresión de Huffman**: lee un `.txt`, calcula la frecuencia de cada carácter, construye el
   árbol de Huffman con la técnica voraz, genera los códigos binarios, codifica el archivo a `.huf`,
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
main.py                     Punto de entrada
huffman/
  frecuencias.py            Lectura del .txt y conteo de frecuencias
  arbol.py                  Nodo y construcción voraz del árbol (heap)
  codigos.py                Recorrido del árbol -> códigos binarios
  codificador.py            Codificar / decodificar y formato de archivo .huf
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

## Pestaña Huffman

1. **Abrir archivo .txt**: calcula frecuencias, construye el árbol y muestra la tabla
   carácter / frecuencia / probabilidad / código / bits. Al seleccionar un carácter se resalta su
   camino en el árbol.
2. **Codificar y guardar .huf**: genera la cadena de bits, la empaqueta en bytes y guarda el archivo
   comprimido (incluye la tabla de frecuencias para poder reconstruir el árbol).
3. **Decodificar .huf → .txt**: lee el `.huf`, reconstruye el árbol, recupera el texto y verifica que
   sea idéntico byte por byte al original.

La pestaña *Resultados de compresión* muestra tamaño original vs comprimido, razón de compresión,
bits promedio por carácter, entropía de Shannon, eficiencia del código y tiempos.

### Formato del archivo `.huf`

| Campo | Tamaño |
|---|---|
| Firma `HUF1` | 4 bytes |
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
