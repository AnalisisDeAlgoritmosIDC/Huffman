# Pruebas y evidencias

Hay tres niveles de pruebas:

1. **Pruebas mínimas de la actividad** — `python pruebas/ejecutar_pruebas.py`. Genera
   [`pruebas/RESULTADOS.md`](pruebas/RESULTADOS.md) y los archivos `.mc` y `.txt` recuperados en
   [`pruebas/salidas/`](pruebas/salidas/).
2. **Pruebas unitarias** — `python -m unittest discover -s tests -v` (18 pruebas).
3. **Pruebas en la página publicada** (https://huffmanificador.pages.dev) — capturas en [`capturas/`](capturas/).

## 1. Texto pequeño (comprobación manual)

Entrada: [`pruebas/1_texto_pequeno.txt`](pruebas/1_texto_pequeno.txt) = `abracadabra` (11 bytes).

**Frecuencias contadas a mano:** a = 5, b = 2, r = 2, c = 1, d = 1.

**Construcción voraz del árbol, a mano** (siempre se unen los dos nodos de menor frecuencia):

| Paso | Cola de prioridad antes del paso | Se unen | Nuevo nodo |
|---|---|---|---|
| 1 | c:1, d:1, b:2, r:2, a:5 | c:1 + d:1 | (cd):2 |
| 2 | b:2, r:2, (cd):2, a:5 | b:2 + r:2 | (br):4 |
| 3 | (cd):2, (br):4, a:5 | (cd):2 + (br):4 | (cdbr):6 |
| 4 | a:5, (cdbr):6 | a:5 + (cdbr):6 | raíz:11 |

**Códigos** (izquierda = 0, derecha = 1): a = `0`, c = `100`, d = `101`, b = `110`, r = `111`.

**Bits:** 5·1 + 2·3 + 2·3 + 1·3 + 1·3 = **23 bits** (contra 88 bits sin comprimir).

**Resultado del programa:** las mismas frecuencias, los mismos códigos y 23 bits
(ver [`pruebas/RESULTADOS.md`](pruebas/RESULTADOS.md) y el desglose byte por byte en [`FORMATO.md`](FORMATO.md)).
La prueba unitaria `test_codigos_prefijo_y_longitud` lo comprueba automáticamente.

## 2. Libro de Project Gutenberg

*Alice's Adventures in Wonderland* (Lewis Carroll, Gutenberg #11), 144,395 bytes:

| Original | Comprimido (.mc) | Ahorrado | Reducción | Símbolos | Bits/símbolo | Entropía |
|---|---|---|---|---|---|---|
| 144,395 B (141.01 KB) | 83,332 B (81.38 KB) | 61,063 B (59.63 KB) | 42.29 % | 73 | 4.587 | 4.546 |

Análisis con 4 libros (`python analisis/medir_rendimiento.py`):

| Libro | Original | .mc | Reducción |
|---|---|---|---|
| Alice in Wonderland | 141.0 KB | 81.4 KB | 42.29 % |
| Hamlet | 159.1 KB | 92.2 KB | 42.04 % |
| Moby Dick | 1.19 MB | 695.2 KB | 42.72 % |
| King James Bible | 4.13 MB | 2.37 MB | 42.74 % |

En la página, el libro se busca con el buscador de Gutenberg (captura `capturas/01_…`).

## 3. Integridad

Cada prueba hace `original.txt → archivo.mc → recuperado.txt` y comprueba:

- **Byte a byte:** el recuperado es idéntico al original.
- **SHA-256:** el hash del recuperado coincide con el que se guardó en el encabezado del `.mc`. Así la integridad
  se puede verificar **sin tener el original** (es lo que hace el Inspector).
- **Detección de daños:** se cambia 1 bit de los datos de un `.mc` y se comprueba que la verificación falla
  (prueba unitaria `test_integridad_detecta_corrupcion` y `pruebas/ejecutar_pruebas.py`).

Resultados: los 3 archivos (texto pequeño, Alice y Persuasion) se recuperan idénticos y con el mismo SHA-256;
el archivo alterado se detecta. Ver [`pruebas/RESULTADOS.md`](pruebas/RESULTADOS.md).

## 4. Archivo no utilizado durante el desarrollo

[`pruebas/4_archivo_nuevo_persuasion.txt`](pruebas/4_archivo_nuevo_persuasion.txt): *Persuasion* de Jane Austen
(Project Gutenberg), que no se usó en ningún momento del desarrollo.

| Original | Comprimido (.mc) | Ahorrado | Reducción | Símbolos | Integridad |
|---|---|---|---|---|---|
| 466,292 B (455.36 KB) | 260,672 B (254.56 KB) | 205,620 B | 44.10 % | 78 | ✔ byte a byte y SHA-256 |

Para la prueba en vivo con un archivo del profesor: abrir la página, arrastrar el `.txt` a la zona de carga,
**COMPRIMIR**, **INSPECCIONAR** y **DESCOMPRIMIR**. El Inspector muestra «✔ Archivo íntegro» si el resultado
coincide con el SHA-256 guardado.

## Casos límite cubiertos por las pruebas unitarias

| Caso | Prueba |
|---|---|
| Un solo carácter distinto (`aaaa`): se le asigna el código `0` | `test_un_solo_caracter` |
| Texto vacío | `test_texto_vacio` (la página además avisa «el archivo está vacío») |
| Unicode, acentos, emoji y saltos `\r\n` | `test_unicode_y_saltos` |
| Longitud promedio entre H y H + 1 | `test_promedio_entre_entropia_y_entropia_mas_uno` |
| Encabezado v2 completo y secciones sin huecos; el texto no aparece en claro | `test_encabezado_v2` |
| Lectura de archivos de la versión 1 | `test_lee_formato_v1` |
| Archivo que no es `.mc` | `test_archivo_invalido` |
| Kruskal y Prim = fuerza bruta | `test_contra_fuerza_bruta`, `test_kruskal_y_prim_coinciden` |
| Detección de idioma en 6 idiomas | `test_muestras` y otras de `test_idioma.py` |
