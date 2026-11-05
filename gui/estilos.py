"""
Colores, fuentes y estilo ttk compartidos por toda la interfaz.
"""
import sys
from tkinter import ttk

# Paleta
FONDO = "#f4f1ea"
PANEL = "#ffffff"
TINTA = "#1f2a44"        # azul marino (texto, nodos internos)
TINTA_SUAVE = "#5b6478"
ACENTO = "#e07a5f"       # coral (resaltados)
HOJA = "#f2cc8f"         # arena (hojas del árbol)
VERDE = "#3d9970"        # aceptado
ROJO = "#c0392b"         # rechazado
GRIS = "#c9c4b8"         # aristas sin evaluar
LINEA = "#8a8f9c"

if sys.platform.startswith("win"):
    FAMILIA = "Segoe UI"
    MONO = "Consolas"
elif sys.platform == "darwin":
    FAMILIA = "Helvetica Neue"
    MONO = "Menlo"
else:
    FAMILIA = "DejaVu Sans"
    MONO = "DejaVu Sans Mono"


def fuente(tamano=10, peso="normal"):
    return (FAMILIA, tamano, peso)


def fuente_mono(tamano=10):
    return (MONO, tamano)


def aplicar_estilo(raiz):
    raiz.configure(bg=FONDO)
    estilo = ttk.Style(raiz)
    try:
        estilo.theme_use("clam")
    except Exception:
        pass

    estilo.configure(".", background=FONDO, foreground=TINTA, font=fuente(10))
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Panel.TFrame", background=PANEL)
    estilo.configure("TLabel", background=FONDO, foreground=TINTA)
    estilo.configure("Panel.TLabel", background=PANEL)
    estilo.configure("Titulo.TLabel", font=fuente(17, "bold"), background=TINTA, foreground="white")
    estilo.configure("Subtitulo.TLabel", font=fuente(10), background=TINTA, foreground="#c8cfdd")
    estilo.configure("Encabezado.TFrame", background=TINTA)
    estilo.configure("Dato.TLabel", font=fuente(10), background=PANEL, foreground=TINTA_SUAVE)
    estilo.configure("Valor.TLabel", font=fuente(11, "bold"), background=PANEL, foreground=TINTA)
    estilo.configure("Grande.TLabel", font=fuente(22, "bold"), background=PANEL, foreground=VERDE)
    estilo.configure("Estado.TLabel", font=fuente(9), background="#e6e1d6", foreground=TINTA_SUAVE, padding=(10, 4))

    estilo.configure("TLabelframe", background=FONDO, bordercolor=GRIS)
    estilo.configure("TLabelframe.Label", background=FONDO, foreground=TINTA, font=fuente(10, "bold"))

    estilo.configure("TButton", padding=(12, 6), background="#e8e4da", bordercolor=GRIS)
    estilo.map("TButton", background=[("active", "#ddd7ca"), ("disabled", "#eeebe4")])
    estilo.configure("Acento.TButton", background=ACENTO, foreground="white", bordercolor=ACENTO,
                     font=fuente(10, "bold"))
    estilo.map("Acento.TButton", background=[("active", "#cf6a50"), ("disabled", "#e9b9ab")],
               foreground=[("disabled", "#fbeee9")])

    estilo.configure("TNotebook", background=FONDO, borderwidth=0)
    estilo.configure("TNotebook.Tab", padding=(16, 7), font=fuente(10))
    estilo.map("TNotebook.Tab", background=[("selected", PANEL)],
               font=[("selected", fuente(10, "bold"))])

    estilo.configure("Treeview", rowheight=24, font=fuente(10), fieldbackground=PANEL, background=PANEL)
    estilo.configure("Treeview.Heading", font=fuente(10, "bold"), background="#e8e4da")
    estilo.map("Treeview", background=[("selected", ACENTO)], foreground=[("selected", "white")])
    return estilo
