"""
Ventana principal: encabezado, pestañas y barra de estado.
"""
import tkinter as tk
from tkinter import ttk

from .estilos import aplicar_estilo
from .tab_huffman import PestanaHuffman
from .tab_mst import PestanaMST


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos voraces · Huffman y Árbol de Expansión Mínima")
        self.geometry("1360x820")
        self.minsize(1100, 680)
        aplicar_estilo(self)

        encabezado = ttk.Frame(self, style="Encabezado.TFrame", padding=(18, 12))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="Algoritmos voraces", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text="Compresión de datos con Huffman  ·  Árbol de expansión mínima "
                                   "(Kruskal y Prim)", style="Subtitulo.TLabel").pack(anchor="w")

        self.estado = tk.StringVar(value="Listo. Abre un archivo .txt para comenzar.")

        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        self.huffman = PestanaHuffman(self.pestanas, self.estado)
        self.mst = PestanaMST(self.pestanas, self.estado)
        self.pestanas.add(self.huffman, text="  Huffman  ")
        self.pestanas.add(self.mst, text="  Árbol de expansión mínima  ")

        ttk.Label(self, textvariable=self.estado, style="Estado.TLabel").pack(fill="x", side="bottom")
