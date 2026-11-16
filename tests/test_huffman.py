import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from huffman import (
    calcular_frecuencias, construir_arbol, generar_codigos, es_codigo_prefijo,
    codificar, decodificar, guardar_comprimido, descomprimir_archivo,
    longitud_promedio, entropia,
)


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

    def test_archivo_huf_ida_y_vuelta(self):
        texto = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme...\n" * 50
        frec, codigos, bits = self.ciclo_completo(texto)
        with tempfile.TemporaryDirectory() as tmp:
            huf = os.path.join(tmp, "x.mc")
            salida = os.path.join(tmp, "x.txt")
            tam = guardar_comprimido(huf, frec, bits, "utf-8")
            self.assertEqual(tam, os.path.getsize(huf))
            self.assertEqual(descomprimir_archivo(huf, salida), texto)
            with open(salida, "rb") as f:
                self.assertEqual(f.read(), texto.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
