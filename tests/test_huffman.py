import hashlib
import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from huffman import (
    calcular_frecuencias, construir_arbol, generar_codigos, es_codigo_prefijo,
    codificar, decodificar, guardar_comprimido, descomprimir_archivo,
    descomprimir_y_verificar, leer_mc, longitud_promedio, entropia,
)
from huffman.codificador import bits_a_bytes


class PruebasHuffman(unittest.TestCase):
    def ciclo_completo(self, texto):
        frec = calcular_frecuencias(texto)
        raiz, _ = construir_arbol(frec)
        codigos = generar_codigos(raiz)
        bits = codificar(texto, codigos)
        self.assertEqual(decodificar(bits, raiz), texto)
        return frec, codigos, bits

    def test_frecuencias(self):
        self.assertEqual(calcular_frecuencias("abracadabra"),
                         {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1})

    def test_codigos_prefijo_y_longitud(self):
        frec, codigos, bits = self.ciclo_completo("abracadabra")
        self.assertTrue(es_codigo_prefijo(codigos))
        # Para abracadabra el costo óptimo de Huffman es 23 bits
        self.assertEqual(len(bits), 23)

    def test_un_solo_caracter(self):
        _, codigos, bits = self.ciclo_completo("aaaa")
        self.assertEqual(codigos, {"a": "0"})
        self.assertEqual(bits, "0000")

    def test_texto_vacio(self):
        raiz, _ = construir_arbol({})
        self.assertIsNone(raiz)
        self.assertEqual(decodificar("", raiz), "")

    def test_unicode_y_saltos(self):
        self.ciclo_completo("¡Hola, señor!\r\nÁrbol ñandú… 🐉\n")

    def test_promedio_entre_entropia_y_entropia_mas_uno(self):
        frec, codigos, _ = self.ciclo_completo("el veloz murciélago hindú comía feliz cardillo y kiwi")
        h = entropia(frec)
        l = longitud_promedio(frec, codigos)
        self.assertLessEqual(h, l + 1e-9)
        self.assertLess(l, h + 1)

    def comprimir_en(self, carpeta, texto, nombre="quijote.txt"):
        frec, _, bits = self.ciclo_completo(texto)
        ruta = os.path.join(carpeta, "x.mc")
        datos = texto.encode("utf-8")
        tam = guardar_comprimido(ruta, frec, bits, "utf-8", datos, nombre)
        return ruta, tam, frec, bits, datos

    def test_archivo_mc_ida_y_vuelta(self):
        texto = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme...\n" * 50
        with tempfile.TemporaryDirectory() as tmp:
            ruta, tam, _, _, datos = self.comprimir_en(tmp, texto)
            salida = os.path.join(tmp, "x.txt")
            self.assertEqual(tam, os.path.getsize(ruta))
            self.assertEqual(descomprimir_archivo(ruta, salida), texto)
            with open(salida, "rb") as f:
                self.assertEqual(f.read(), datos)

    def test_encabezado_v2(self):
        texto = "¡Hola, señor! Árbol ñandú.\n" * 20
        with tempfile.TemporaryDirectory() as tmp:
            ruta, tam, frec, bits, datos = self.comprimir_en(tmp, texto, "prueba ñ.txt")
            with open(ruta, "rb") as f:
                crudo = f.read()
            self.assertEqual(crudo[:4], b"HMC\x02")
            info = leer_mc(ruta)
            self.assertEqual(info["version"], 2)
            self.assertEqual(info["tamano_original"], len(datos))
            self.assertEqual(info["caracteres"], len(texto))
            self.assertEqual(info["bits_validos"], len(bits))
            self.assertEqual(info["relleno"], (8 - len(bits) % 8) % 8)
            self.assertEqual(info["sha256"], hashlib.sha256(datos).hexdigest())
            self.assertEqual(info["nombre_original"], "prueba ñ.txt")
            self.assertEqual(info["frecuencias"], frec)
            self.assertEqual(info["simbolos"], len(frec))
            self.assertEqual(info["tamano_comprimido"], tam)
            # Las secciones cubren el archivo completo sin huecos
            fin = 0
            for _, offset, largo in info["secciones"]:
                self.assertEqual(offset, fin)
                fin += largo
            self.assertEqual(fin, tam)
            # El .mc no guarda el texto original en claro
            self.assertNotIn(b"Hola, se", crudo)

    def test_integridad_detecta_corrupcion(self):
        texto = "abracadabra pata de cabra " * 40
        with tempfile.TemporaryDirectory() as tmp:
            ruta, *_ = self.comprimir_en(tmp, texto)
            _, ok = descomprimir_y_verificar(ruta)
            self.assertTrue(ok["sha256_ok"])
            self.assertTrue(ok["tamano_ok"])
            with open(ruta, "rb") as f:
                crudo = bytearray(f.read())
            crudo[-3] ^= 0b00010000          # se cambia un bit de los datos
            with open(ruta, "wb") as f:
                f.write(crudo)
            _, mal = descomprimir_y_verificar(ruta)
            self.assertFalse(mal["sha256_ok"])

    def test_lee_formato_v1(self):
        texto = "version uno del formato\n" * 10
        frec, _, bits = self.ciclo_completo(texto)
        datos, relleno = bits_a_bytes(bits)
        crudo = b"HMC1" + bytes([5]) + b"utf-8" + struct.pack(">I", len(frec))
        for c, f in frec.items():
            b = c.encode("utf-8")
            crudo += bytes([len(b)]) + b + struct.pack(">I", f)
        crudo += bytes([relleno]) + datos
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "viejo.mc")
            with open(ruta, "wb") as f:
                f.write(crudo)
            self.assertEqual(leer_mc(ruta)["version"], 1)
            self.assertEqual(descomprimir_archivo(ruta), texto)

    def test_archivo_invalido(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "malo.mc")
            with open(ruta, "wb") as f:
                f.write(b"esto no es un archivo mc")
            with self.assertRaises(ValueError):
                leer_mc(ruta)


if __name__ == "__main__":
    unittest.main()
