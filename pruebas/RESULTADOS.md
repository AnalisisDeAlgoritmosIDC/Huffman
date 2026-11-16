# Resultados de las pruebas (generado por `pruebas/ejecutar_pruebas.py`)

Flujo de cada prueba: `original.txt → archivo.mc → recuperado.txt`. Los archivos generados están en
`pruebas/salidas/`.

## Resumen

| Prueba | Archivo | Original | Comprimido (.mc) | Ahorrado | Reducción | Símbolos | Byte a byte | SHA-256 |
|---|---|---|---|---|---|---|---|---|
| 1. Texto pequeño | `1_texto_pequeno.txt` | 11 B (0.01 KB) | 133 B (0.13 KB) | -122 B | -1109.09 % | 5 | ✔ idéntico | ✔ |
| 2. Libro de Project Gutenberg (Alice, #11) | `alice_in_wonderland.txt` | 144,395 B (141.01 KB) | 83,332 B (81.38 KB) | 61,063 B | 42.29 % | 73 | ✔ idéntico | ✔ |
| 4. Archivo no usado en el desarrollo (Persuasion, J. Austen) | `4_archivo_nuevo_persuasion.txt` | 466,292 B (455.36 KB) | 260,672 B (254.56 KB) | 205,620 B | 44.10 % | 78 | ✔ idéntico | ✔ |

## 1. Texto pequeño: «abracadabra»

Frecuencias y códigos que genera el programa (se comprueban a mano en `PRUEBAS.md`):

| Símbolo | Frecuencia | Código | Bits × frecuencia |
|---|---|---|---|
| `a` | 5 | `0` | 1 × 5 = 5 |
| `b` | 2 | `110` | 3 × 2 = 6 |
| `r` | 2 | `111` | 3 × 2 = 6 |
| `c` | 1 | `100` | 3 × 1 = 3 |
| `d` | 1 | `101` | 3 × 1 = 3 |

Total: **23 bits** de datos codificados (vs. 88 bits sin comprimir). El .mc pesa 133 bytes porque su encabezado y tabla ocupan más que el texto: con textos tan pequeños el archivo comprimido es **más grande** que el original (ver «Limitaciones» en el README).

## 3. Integridad

| Archivo | SHA-256 del original | SHA-256 del recuperado | Igual |
|---|---|---|---|
| `1_texto_pequeno.txt` | `045babdcd2118960e8c8b8e0…` | `045babdcd2118960e8c8b8e0…` | ✔ |
| `alice_in_wonderland.txt` | `5ce9042c0d8536b072b61d4c…` | `5ce9042c0d8536b072b61d4c…` | ✔ |
| `4_archivo_nuevo_persuasion.txt` | `cec097657cbfeb62aafe1789…` | `cec097657cbfeb62aafe1789…` | ✔ |

**Archivo alterado:** se cambió 1 bit en los datos de `alice_in_wonderland.mc`. Al descomprimirlo, el SHA-256 del resultado NO coincide con el guardado en el encabezado → la página marca el archivo como dañado.

## Tiempos (Python 3, computadora de desarrollo)

| Archivo | Bits codificados | Bits/símbolo | Entropía | Comprimir | Descomprimir |
|---|---|---|---|---|---|
| `1_texto_pequeno.txt` | 23 | 2.0909 | 2.0404 | 0.001 s | 0.001 s |
| `alice_in_wonderland.txt` | 662,314 | 4.5868 | 4.5459 | 0.016 s | 0.039 s |
| `4_archivo_nuevo_persuasion.txt` | 2,080,738 | 4.4623 | 4.4307 | 0.050 s | 0.121 s |
