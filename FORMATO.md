# Formato de archivo `.mc` (versión 2)

`.mc` es el formato propio de **El Huffmanificador** para guardar un texto comprimido con Huffman.
El archivo **no contiene el texto original**: contiene un encabezado con metadatos, la tabla de frecuencias
necesaria para reconstruir el árbol y los bits codificados empaquetados en bytes. Con eso basta para
descomprimirlo sin tener el `.txt`.

La implementación está en [`huffman/codificador.py`](huffman/codificador.py) (`guardar_comprimido`, `leer_mc`,
`descomprimir_y_verificar`).

## Estructura

Todos los enteros se guardan en **big-endian** (el byte más significativo primero).

| Offset | Bytes | Campo | Para qué sirve |
|---:|---:|---|---|
| 0 | 3 | Firma `HMC` (`48 4D 43`) | Identifica el archivo como «Huffmanificador Comprimido» |
| 3 | 1 | Versión del formato (`02`) | Permite cambiar el formato sin romper archivos viejos |
| 4 | 8 | Tamaño del archivo original (bytes) | Métricas y verificación de integridad |
| 12 | 8 | Número de caracteres del texto | Métricas; también es la frecuencia de la raíz del árbol |
| 20 | 8 | Total de bits codificados válidos | Saber exactamente dónde terminan los datos |
| 28 | 1 | Bits de relleno del último byte (0-7) | Ignorar los ceros agregados para completar el último byte |
| 29 | 8 | Fecha de creación (segundos desde 1970, UTC) | Metadato |
| 37 | 32 | SHA-256 del archivo original | **Integridad**: el resultado de descomprimir debe tener el mismo hash |
| 69 | 1 | Largo L1 del nombre de la codificación | |
| 70 | L1 | Codificación del texto (`utf-8` o `latin-1`) | Volver a escribir exactamente los mismos bytes |
| 70+L1 | 2 | Largo L2 del nombre del archivo original | |
| 72+L1 | L2 | Nombre del archivo original (UTF-8) | Metadato y nombre sugerido al descargar |
| … | 4 | Número de símbolos distintos K | Inicio de la **tabla de frecuencias** |
| … | K × (1 + n + 4) | Por símbolo: largo n en UTF-8 (1 B), el símbolo (n B), su frecuencia (4 B) | Reconstruir el árbol de Huffman |
| … | ⌈bits / 8⌉ | **Datos comprimidos**: los códigos de Huffman concatenados y empaquetados en bytes | |

### Por qué se guarda la tabla de frecuencias y no los códigos

La tabla de frecuencias es compacta (unos 9 bytes por símbolo en un libro en inglés) y, como la construcción
del árbol es **determinista** (las hojas entran a la cola de prioridad ordenadas por frecuencia y luego por
carácter, y los empates se resuelven con un contador), al repetir el algoritmo voraz con la misma tabla se
obtiene exactamente el mismo árbol y los mismos códigos que se usaron para comprimir.

### Cómo se descomprime

1. Se verifica la firma `HMC` y la versión.
2. Se leen el encabezado y la tabla de frecuencias.
3. Se reconstruye el árbol de Huffman con la tabla (mismo algoritmo voraz).
4. Se leen los datos, se convierten a bits y se descartan los bits de relleno del final.
5. Se recorre el árbol bit por bit (0 = izquierda, 1 = derecha); al llegar a una hoja se escribe su símbolo y se
   regresa a la raíz.
6. El texto se codifica con la codificación guardada y se comparan el **tamaño** y el **SHA-256** con los del
   encabezado. Si no coinciden, el archivo está dañado o fue modificado.

## Ejemplo completo: «abracadabra»

Archivo [`pruebas/salidas/1_texto_pequeno.mc`](pruebas/salidas/1_texto_pequeno.mc), 133 bytes:

```
00000000  48 4d 43 02 00 00 00 00 00 00 00 0b 00 00 00 00  HMC.............
00000010  00 00 00 0b 00 00 00 00 00 00 00 17 01 00 00 00  ................
00000020  00 6a fb 55 8b 04 5b ab dc d2 11 89 60 e8 c8 b8  .j.U..[.....`...
00000030  e0 ec f6 5b 73 46 86 e1 b1 8f 58 71 0c 96 46 77  ...[sF....Xq..Fw
00000040  9f 49 e9 42 ae 05 75 74 66 2d 38 00 13 31 5f 74  .I.B..utf-8..1_t
00000050  65 78 74 6f 5f 70 65 71 75 65 6e 6f 2e 74 78 74  exto_pequeno.txt
00000060  00 00 00 05 01 61 00 00 00 05 01 62 00 00 00 02  .....a.....b....
00000070  01 72 00 00 00 02 01 63 00 00 00 01 01 64 00 00  .r.....c.....d..
00000080  00 01 6e 8a dc                                   ..n..
```

| Bytes | Valor | Significado |
|---|---|---|
| `48 4d 43` `02` | `HMC`, 2 | Firma y versión 2 |
| `00 … 0b` | 11 | Tamaño original: 11 bytes |
| `00 … 0b` | 11 | 11 caracteres |
| `00 … 17` | 23 | 23 bits válidos |
| `01` | 1 | 1 bit de relleno en el último byte |
| `00 00 00 00 6a fb 55 8b` | fecha | Fecha de creación |
| `04 5b ab … 42 ae` | SHA-256 | Hash del original (`045babdc…f49e942ae`) |
| `05` `utf-8` | | Codificación |
| `00 13` `1_texto_pequeno.txt` | 19 | Nombre original |
| `00 00 00 05` | 5 | 5 símbolos |
| `01 61 00 00 00 05` | `a`: 5 | Tabla: `a` aparece 5 veces |
| `01 62 00 00 00 02` | `b`: 2 | |
| `01 72 00 00 00 02` | `r`: 2 | |
| `01 63 00 00 00 01` | `c`: 1 | |
| `01 64 00 00 00 01` | `d`: 1 | |
| `6e 8a dc` | `01101110 10001010 11011100` | Datos: 23 bits + 1 de relleno |

Los 23 bits `0 110 111 0 100 0 101 0 110 111 0` son `a b r a c a d a b r a` con los códigos
`a=0, b=110, r=111, c=100, d=101`. El último `0` de `11011100` es relleno y se ignora.

> En un texto tan pequeño el `.mc` (133 B) es más grande que el original (11 B), porque el encabezado y la tabla
> ocupan más que el texto. En un libro, ese costo fijo es despreciable (≈ 560 bytes de 83 KB en *Alice*).

## Versión 1 (compatibilidad)

Los archivos de la primera versión empezaban con `HMC1` y solo guardaban la codificación, la tabla de
frecuencias, el relleno y los datos (sin tamaño original, hash, fecha ni nombre). La página y `leer_mc()` todavía
los pueden abrir; el Inspector indica que esos campos no están disponibles.
