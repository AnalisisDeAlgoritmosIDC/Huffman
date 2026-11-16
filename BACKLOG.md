# Backlog para GitHub Projects

Tablero sugerido: **Projects → New project → Board**, con estas columnas (Settings → Status):

`Backlog` → `Por hacer` → `En progreso` → `En revisión` → `Terminado`

Para cada fila de abajo: **+ Add item** en la columna correspondiente, pegar el título y, al abrir el elemento,
copiar la descripción y el resultado esperado y asignar al responsable (campo *Assignees*). Si lo convierten en
*issue* (botón «Convert to issue»), los commits pueden cerrarlo escribiendo `closes #N` en el mensaje.

**C** = Carlos Adrian Ramirez Gutiérrez · **I** = Isaac Saldivar Zaldivar · **D** = Daniel Padilla Echeverria

## Trabajo algorítmico

| # | Tarea | Responsable | Qué se hará | Resultado esperado | Estado |
|---|---|---|---|---|---|
| 1 | Cálculo de frecuencias | I | Leer el .txt (UTF-8 / Latin-1, en binario) y contar cada carácter | `huffman/frecuencias.py` con `leer_texto` y `calcular_frecuencias` | Terminado |
| 2 | Cola de prioridad y árbol voraz | I | Construir el árbol uniendo siempre los dos nodos de menor frecuencia con `heapq` | `huffman/arbol.py`, árbol determinista y O(n log n) | Terminado |
| 3 | Generación de códigos | I | Recorrer el árbol (0 = izquierda, 1 = derecha), caso de un solo símbolo | `huffman/codigos.py`, código prefijo | Terminado |
| 4 | Empaquetado de bits | I | Convertir la cadena de bits en bytes y registrar el relleno del último byte | `bits_a_bytes` / `bytes_a_bits` | Terminado |
| 5 | Formato propio .mc v2 | I + C | Diseñar encabezado (firma, versión, tamaño original, bits, relleno, fecha, SHA-256, nombre) y tabla | `FORMATO.md` + `guardar_comprimido` / `leer_mc` | Terminado |
| 6 | Descompresor con verificación | I | Reconstruir el árbol desde la tabla, decodificar y comparar tamaño y SHA-256 | `descomprimir_y_verificar`, detecta archivos alterados | Terminado |
| 7 | Métricas y entropía | I | Longitud promedio, entropía de Shannon, razón y porcentaje | `huffman/estadisticas.py` | Terminado |
| 8 | Detección de idioma | I | Palabras vacías ponderadas de 8 idiomas + letras características | `idioma/detector.py` | Terminado |
| 9 | Grafo aleatorio conexo | D | Generar grafos ponderados para el árbol de expansión mínima | `mst/grafo.py` | Terminado |
| 10 | Kruskal con Union-Find | D | Ordenar aristas y evitar ciclos | `mst/kruskal.py` | Terminado |
| 11 | Prim con heap | D | Crecer el árbol desde un nodo inicial | `mst/prim.py` | Terminado |

## Trabajo de ingeniería

| # | Tarea | Responsable | Qué se hará | Resultado esperado | Estado |
|---|---|---|---|---|---|
| 12 | Python en el navegador | I | Cargar Pyodide y los módulos .py; puente JS ↔ Python | `web/python.js`, `web/puente.py` | Terminado |
| 13 | Integración con Project Gutenberg | D | Buscar por título/autor/palabras y descargar el .txt (servidor intermedio por CORS) | `worker/index.js`, `functions/api/[[ruta]].js`, `web/buscador.js` | Terminado |
| 14 | Interfaz y diseño | C | Página con tema morado tinto, métricas, carga de archivos, avisos | `index.html`, `web/styles.css` | Terminado |
| 15 | Barra de flujo | D | Mostrar BUSCAR/SUBIR → ANALIZAR → CONSTRUIR → COMPRIMIR → INSPECCIONAR → DESCOMPRIMIR | `web/flujo.js` | Terminado |
| 16 | Visualización del árbol | C + D | Vistas jerárquica, explorador, radial y construcción paso a paso | `web/arbol.js`, `web/arbol_radial.js`, `web/construccion.js` | Terminado |
| 17 | Ahorro interactivo | C | Curva de bits, carácter por carácter, contribución por símbolo y calculadora | `web/ahorro.js` | Terminado |
| 18 | Inspector de archivos .mc | C | Examinar un .mc sin el original (metadatos, mapa de bytes, hex, bits, tabla, árbol) y descomprimir aparte | `web/inspector.js` | Terminado |
| 19 | Sección de Huffman | C | Flujo comprimir / inspeccionar / descomprimir y resultados | `web/huffman_ui.js` | Terminado |
| 20 | Sección de expansión mínima | D | Kruskal / Prim paso a paso con bitácora | `web/mst_ui.js` | Terminado |
| 21 | Pruebas unitarias | I + D | Casos límite, formato, integridad, MST contra fuerza bruta, idioma | `tests/` (18 pruebas) | Terminado |
| 22 | Pruebas mínimas documentadas | D | Texto pequeño, libro, integridad y archivo nuevo | `pruebas/`, `PRUEBAS.md` | Terminado |
| 23 | Análisis de rendimiento | D | Medir 4 libros y Kruskal vs. Prim | `analisis/` | Terminado |
| 24 | Deployment | D + C | Cloudflare Pages conectado a GitHub | https://huffmanificador.pages.dev | Terminado |
| 25 | Documentación | C + I | README, FORMATO.md, uso de IA, limitaciones | `README.md`, `FORMATO.md` | Terminado |
| 26 | Reporte técnico | C | Reporte breve en PDF según la Guía de Reportes | `reporte/Reporte_Huffman_MST.pdf` | Terminado |
| 27 | Prueba en vivo | C + I + D | Probar en la revisión con un .txt del profesor | Archivo recuperado idéntico | Por hacer |
