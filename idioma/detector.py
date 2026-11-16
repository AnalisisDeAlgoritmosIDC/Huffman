"""
Detección del idioma de un texto.

Método: se cuentan las "palabras vacías" (stopwords) más comunes de cada
idioma (artículos, preposiciones, conjunciones...). Esas palabras forman
cerca de la mitad de cualquier texto, así que el idioma cuyo vocabulario
aparece más veces es, casi siempre, el idioma del texto. Se suma un pequeño
puntaje por letras propias de cada idioma (ñ, ç, ß, ã...).

Si el texto viene de Project Gutenberg, primero se quita el encabezado y la
licencia (que siempre están en inglés) y se lee el campo "Language:".
"""
import re
from collections import Counter

NOMBRES = {
    "es": "Español", "en": "Inglés", "fr": "Francés", "de": "Alemán",
    "it": "Italiano", "pt": "Portugués", "nl": "Neerlandés", "la": "Latín",
}

PALABRAS = {
    "es": """de la que el en y a los se del las un por con no una su para es al lo como más pero sus le
             ya o fue este ha sí porque esta son entre cuando muy sin sobre también me hasta hay donde quien
             desde todo nos durante todos uno les ni contra otros ese eso ante ellos esto antes algunos qué
             unos yo otro otras otra él tanto esa estos mucho quienes nada muchos cual poco ella estar
             estas algunas algo nosotros mi mis tú te ti tu tus ellas vuestra dijo había era señor""",
    "en": """the of and to in a is that it was he for on are as with his they i at be this have from or
             one had by but not what all were we when your can said there an each which she do how their
             if will up other about out many then them these so some her would make like him into has
             two more no could my than been who its did you me upon""",
    "fr": """de la le et les des en un du une que est pour qui dans par plus pas au sur ne se ce il sont
             avec son elle nous vous je mais ou comme on tout aux lui ses leur été cette fait bien sans
             était avait dit mon ma moi""",
    "de": """der die und in den von zu das mit sich des auf für ist im dem nicht ein eine als auch es an
             werden aus er hat dass sie nach wird bei einer um am sind noch wie einem über einen so zum
             war haben nur oder aber vor zur bis mehr durch man ich wir ihr""",
    "it": """di e il la che in a per un è del non sono le si con da una i lo al gli come ma più anche
             dei della nel alla ha questo se mi io ci suo sua delle cosa quando era aveva egli""",
    "pt": """de a o que e do da em um para é com não uma os no se na por mais as dos como mas foi ao
             ele das tem à seu sua ou ser quando muito há nos já está eu também só pelo pela até isso ela
             entre era depois sem mesmo aos você então""",
    "nl": """de en van het een in is dat op te zijn met voor niet aan er die maar om ook als dan bij nog
             uit wat ze zo hij was had""",
    "la": """et in est non ad cum quod sed ut qui quae de ex per esse sunt enim nec atque vel autem hoc
             eius quam ab sicut""",
}
PALABRAS = {cod: set(lista.split()) for cod, lista in PALABRAS.items()}

# Peso de cada palabra: si la comparten k idiomas, vale 1/k para cada uno.
# Así "de" (es, fr, pt, nl, la) casi no decide nada y "the" o "und" deciden mucho.
_REPETICION = Counter(p for vocabulario in PALABRAS.values() for p in vocabulario)
PESO = {p: 1 / k for p, k in _REPETICION.items()}

LETRAS = {
    "es": "ñ¿¡", "pt": "ãõç", "fr": "çœàèùâêîôû", "de": "ßäöü", "it": "àèìòù",
}

GUTENBERG_IDIOMAS = {
    "spanish": "es", "english": "en", "french": "fr", "german": "de", "italian": "it",
    "portuguese": "pt", "dutch": "nl", "latin": "la",
}

MAX_PALABRAS = 60000


def quitar_gutenberg(texto):
    """Regresa (cuerpo_del_libro, idioma_declarado_o_None)."""
    declarado = None
    m = re.search(r"^Language:\s*([A-Za-z]+)", texto[:20000], re.MULTILINE)
    if m:
        declarado = m.group(1).strip()
    inicio = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG E-?BOOK[^\n]*\n", texto, re.IGNORECASE)
    fin = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG E-?BOOK", texto, re.IGNORECASE)
    if inicio:
        texto = texto[inicio.end(): fin.start() if fin and fin.start() > inicio.end() else None]
    return texto, declarado


def detectar_idioma(texto):
    """Regresa un diccionario con el idioma detectado, la confianza y el ranking."""
    cuerpo, declarado = quitar_gutenberg(texto)
    palabras = re.findall(r"[^\W\d_]+", cuerpo.lower())[:MAX_PALABRAS]
    total = len(palabras)
    conteo = Counter(palabras)

    puntajes = {}
    cobertura = {}
    encontradas = {}
    for cod, vocabulario in PALABRAS.items():
        aciertos = {p: conteo[p] for p in vocabulario if p in conteo}
        puntajes[cod] = sum(n * PESO[p] for p, n in aciertos.items()) / total if total else 0.0
        cobertura[cod] = sum(aciertos.values()) / total if total else 0.0
        encontradas[cod] = sorted(aciertos.items(), key=lambda x: -x[1])[:10]

    # Bonus por letras características
    letras = Counter(c for c in cuerpo[:400000].lower() if c.isalpha())
    total_letras = sum(letras.values()) or 1
    especiales = {}
    for cod, caracteres in LETRAS.items():
        cantidad = sum(letras[c] for c in caracteres)
        especiales[cod] = [c for c in caracteres if letras[c]]
        puntajes[cod] += min(0.03, cantidad / total_letras * 2)

    # Probabilidad relativa: se elevan los puntajes al cuadrado para que el
    # idioma claramente dominante se separe de los que solo comparten palabras
    cuadrados = {cod: v * v for cod, v in puntajes.items()}
    suma = sum(cuadrados.values()) or 1
    ranking = sorted(((cod, cuadrados[cod] / suma * 100) for cod in puntajes), key=lambda x: -x[1])
    ganador, porcentaje = ranking[0]

    if total < 5 or cobertura[ganador] < 0.05:
        ganador = None

    declarado_cod = GUTENBERG_IDIOMAS.get((declarado or "").lower())
    return {
        "codigo": ganador,
        "nombre": NOMBRES.get(ganador, "No identificado"),
        "confianza": porcentaje if ganador else 0.0,
        "cobertura": cobertura[ranking[0][0]] * 100,   # % del texto que son palabras vacías del idioma
        "ranking": [[cod, NOMBRES[cod], round(p, 2)] for cod, p in ranking],
        "palabras_clave": encontradas.get(ganador, []) if ganador else [],
        "letras_especiales": especiales.get(ganador, []) if ganador else [],
        "palabras_analizadas": total,
        "declarado_gutenberg": declarado,
        "coincide_con_gutenberg": (declarado_cod == ganador) if declarado_cod else None,
    }
