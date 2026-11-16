import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from idioma import detectar_idioma

MUESTRAS = {
    "es": "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un "
          "hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor. Una olla de algo "
          "más vaca que carnero, salpicón las más noches, duelos y quebrantos los sábados.",
    "en": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of "
          "foolishness, it was the epoch of belief, it was the epoch of incredulity, and we had everything before us.",
    "fr": "Longtemps, je me suis couché de bonne heure. Parfois, à peine ma bougie éteinte, mes yeux se fermaient "
          "si vite que je n'avais pas le temps de me dire: Je m'endors. Et, une demi-heure après, la pensée qu'il "
          "était temps de chercher le sommeil m'éveillait.",
    "de": "Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in seinem Bett zu einem "
          "ungeheueren Ungeziefer verwandelt. Er lag auf seinem panzerartig harten Rücken und sah, wenn er den "
          "Kopf ein wenig hob, seinen gewölbten, braunen Bauch.",
    "it": "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, ché la diritta via era smarrita. "
          "Ahi quanto a dir qual era è cosa dura esta selva selvaggia e aspra e forte che nel pensier rinova la paura!",
    "pt": "Ao verme que primeiro roeu as frias carnes do meu cadáver dedico como saudosa lembrança estas memórias "
          "póstumas. Algum tempo hesitei se devia abrir estas memórias pelo princípio ou pelo fim, isto é, se "
          "poria em primeiro lugar o meu nascimento ou a minha morte.",
}


class PruebasIdioma(unittest.TestCase):
    def test_muestras(self):
        for codigo, texto in MUESTRAS.items():
            with self.subTest(idioma=codigo):
                self.assertEqual(detectar_idioma(texto)["codigo"], codigo)

    def test_libro_ingles(self):
        with open(os.path.join(RAIZ, "libros", "alice_in_wonderland.txt"), encoding="utf-8") as f:
            r = detectar_idioma(f.read())
        self.assertEqual(r["codigo"], "en")
        self.assertGreater(r["confianza"], 50)

    def test_encabezado_gutenberg_en_ingles_no_confunde(self):
        texto = ("The Project Gutenberg eBook of Don Quijote\n\nThis eBook is for the use of anyone anywhere in "
                 "the United States and most other parts of the world at no cost.\n\nLanguage: Spanish\n\n"
                 "*** START OF THE PROJECT GUTENBERG EBOOK DON QUIJOTE ***\n" + MUESTRAS["es"] * 3 +
                 "\n*** END OF THE PROJECT GUTENBERG EBOOK DON QUIJOTE ***\nThe Project Gutenberg License "
                 "and all of the terms of this agreement apply to the work and to you.")
        r = detectar_idioma(texto)
        self.assertEqual(r["codigo"], "es")
        self.assertEqual(r["declarado_gutenberg"], "Spanish")
        self.assertTrue(r["coincide_con_gutenberg"])

    def test_texto_sin_palabras(self):
        self.assertIsNone(detectar_idioma("12345 !!! ???")["codigo"])


if __name__ == "__main__":
    unittest.main()
