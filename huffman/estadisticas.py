"""
Métricas para evaluar la eficiencia de la compresión.
"""
import math


def longitud_promedio(frecuencias, codigos):
    """Bits promedio por carácter: sum(f_i * len(c_i)) / sum(f_i)."""
    total = sum(frecuencias.values())
    if total == 0:
        return 0.0
    return sum(f * len(codigos[c]) for c, f in frecuencias.items()) / total


def entropia(frecuencias):
    """Entropía de Shannon en bits/carácter: límite teórico de compresión."""
    total = sum(frecuencias.values())
    if total == 0:
        return 0.0
    h = 0.0
    for f in frecuencias.values():
        p = f / total
        h -= p * math.log2(p)
    return h


def comparar_tamanos(tamano_original, tamano_comprimido):
    """Regresa un diccionario con la razón y el porcentaje de ahorro."""
    if tamano_original == 0:
        return {"razon": 0.0, "ahorro": 0.0, "porcentaje_del_original": 0.0}
    return {
        "razon": tamano_original / tamano_comprimido if tamano_comprimido else 0.0,
        "ahorro": (1 - tamano_comprimido / tamano_original) * 100,
        "porcentaje_del_original": tamano_comprimido / tamano_original * 100,
    }


def formatear_bytes(n):
    """1536 -> '1.50 KB'"""
    for unidad in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidad == "GB":
            return ("%d %s" % (n, unidad)) if unidad == "B" else ("%.2f %s" % (n, unidad))
        n /= 1024.0
