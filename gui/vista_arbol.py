"""
Widget que dibuja el árbol de Huffman en un Canvas con scroll, zoom y
resaltado del camino de un carácter.
"""
import tkinter as tk
from tkinter import ttk

from huffman import describir_caracter
from . import estilos as E


class VistaArbol(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Panel.TFrame")
        self.raiz = None
        self.escala = 1.0
        self.ids_nodo = {}       # id(nodo) -> id del óvalo/rectángulo en el canvas
        self.ids_arista = {}     # (id(padre), id(hijo)) -> id de la línea
        self.resaltados = []

        barra = ttk.Frame(self, style="Panel.TFrame")
        barra.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Button(barra, text="Zoom +", command=lambda: self.zoom(1.25)).pack(side="left")
        ttk.Button(barra, text="Zoom −", command=lambda: self.zoom(0.8)).pack(side="left", padx=4)
        ttk.Button(barra, text="Restablecer", command=lambda: self.zoom(None)).pack(side="left")
        self.info = ttk.Label(barra, text="Abre un archivo para ver el árbol", style="Dato.TLabel")
        self.info.pack(side="right")

        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.canvas = tk.Canvas(marco, bg=E.PANEL, highlightthickness=0)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.canvas.yview)
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        # Arrastrar para mover y rueda para desplazar
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.canvas.bind("<MouseWheel>", self._rueda)
        self.canvas.bind("<Shift-MouseWheel>", self._rueda_horizontal)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))

    # ------------------------------------------------------------------ eventos
    def _rueda(self, evento):
        self.canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")

    def _rueda_horizontal(self, evento):
        self.canvas.xview_scroll(-1 if evento.delta > 0 else 1, "units")

    def zoom(self, factor):
        self.escala = 1.0 if factor is None else max(0.3, min(3.0, self.escala * factor))
        if self.raiz is not None:
            self.dibujar(self.raiz)

    # ------------------------------------------------------------------ dibujo
    def _calcular_posiciones(self, raiz):
        """Hojas de izquierda a derecha (recorrido en orden); cada nodo
        interno queda centrado sobre sus hijos. Regresa {id(nodo): (x, nivel)}."""
        posiciones = {}
        siguiente_hoja = [0]

        def visitar(nodo, nivel):
            if nodo.es_hoja():
                posiciones[id(nodo)] = (siguiente_hoja[0], nivel)
                siguiente_hoja[0] += 1
                return siguiente_hoja[0] - 1
            xs = []
            for hijo in (nodo.izquierda, nodo.derecha):
                if hijo is not None:
                    xs.append(visitar(hijo, nivel + 1))
            x = sum(xs) / len(xs)
            posiciones[id(nodo)] = (x, nivel)
            return x

        visitar(raiz, 0)
        return posiciones, siguiente_hoja[0]

    def dibujar(self, raiz):
        self.raiz = raiz
        c = self.canvas
        c.delete("all")
        self.ids_nodo.clear()
        self.ids_arista.clear()
        self.resaltados = []
        if raiz is None:
            return

        s = self.escala
        sep_x, sep_y, radio, margen = 46 * s, 74 * s, 17 * s, 40
        posiciones, num_hojas = self._calcular_posiciones(raiz)

        def coord(nodo):
            x, nivel = posiciones[id(nodo)]
            return margen + x * sep_x + radio, margen + nivel * sep_y + radio

        f_peq = E.fuente(max(6, int(8 * s)))
        f_car = E.fuente(max(7, int(11 * s)), "bold")
        f_bit = E.fuente(max(6, int(8 * s)), "bold")

        # Primero las aristas (para que queden debajo de los nodos)
        pila = [raiz]
        nodos = []
        while pila:
            nodo = pila.pop()
            nodos.append(nodo)
            x1, y1 = coord(nodo)
            for bit, hijo in (("0", nodo.izquierda), ("1", nodo.derecha)):
                if hijo is None:
                    continue
                x2, y2 = coord(hijo)
                linea = c.create_line(x1, y1, x2, y2, fill=E.LINEA, width=max(1, 1.2 * s))
                self.ids_arista[(id(nodo), id(hijo))] = linea
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                desplaza = -9 * s if bit == "0" else 9 * s
                c.create_text(mx + desplaza, my - 4 * s, text=bit, fill=E.ACENTO, font=f_bit)
                pila.append(hijo)

        for nodo in nodos:
            x, y = coord(nodo)
            if nodo.es_hoja():
                figura = c.create_rectangle(x - radio, y - radio, x + radio, y + radio,
                                            fill=E.HOJA, outline=E.TINTA, width=1)
                texto = describir_caracter(nodo.caracter)
                texto = texto.split(" ")[0] if len(texto) > 2 else texto
                c.create_text(x, y, text=texto, font=f_car, fill=E.TINTA)
                c.create_text(x, y + radio + 9 * s, text=str(nodo.frecuencia), font=f_peq, fill=E.TINTA_SUAVE)
            else:
                figura = c.create_oval(x - radio, y - radio, x + radio, y + radio,
                                       fill=E.TINTA, outline=E.TINTA)
                c.create_text(x, y, text=str(nodo.frecuencia), font=f_peq, fill="white")
            self.ids_nodo[id(nodo)] = figura

        ancho = margen * 2 + num_hojas * sep_x + radio
        alto = margen * 2 + (max(n for _, n in posiciones.values()) + 1) * sep_y
        c.configure(scrollregion=(0, 0, ancho, alto))
        # Centrar la vista horizontalmente en la raíz
        x_raiz, _ = coord(raiz)
        vis_w = c.winfo_width()
        c.xview_moveto(max(0, (x_raiz - vis_w / 2) / ancho) if ancho > vis_w else 0)
        c.yview_moveto(0)
        self.info.configure(text="%d hojas · zoom %.0f%% · arrastra para moverte" % (num_hojas, s * 100))

    def resaltar(self, codigo):
        """Pinta el camino raíz -> hoja que corresponde a `codigo`."""
        c = self.canvas
        for elemento, tipo in self.resaltados:
            if tipo == "linea":
                c.itemconfigure(elemento, fill=E.LINEA, width=max(1, 1.2 * self.escala))
            else:
                c.itemconfigure(elemento, outline=E.TINTA, width=1)
        self.resaltados = []
        if self.raiz is None or not codigo:
            return

        nodo = self.raiz
        for bit in codigo:
            hijo = nodo.izquierda if bit == "0" else nodo.derecha
            if hijo is None:
                break
            linea = self.ids_arista.get((id(nodo), id(hijo)))
            if linea:
                c.itemconfigure(linea, fill=E.ACENTO, width=4 * self.escala)
                self.resaltados.append((linea, "linea"))
            nodo = hijo
        figura = self.ids_nodo.get(id(nodo))
        if figura:
            c.itemconfigure(figura, outline=E.ACENTO, width=4)
            self.resaltados.append((figura, "figura"))
            # Desplazar la vista para que la hoja quede visible
            x1, y1, x2, y2 = c.coords(figura)
            _, _, ancho, alto = map(float, c.cget("scrollregion").split())
            vis_w, vis_h = c.winfo_width(), c.winfo_height()
            if ancho > vis_w:
                c.xview_moveto(max(0, (x1 - vis_w / 2) / ancho))
            if alto > vis_h:
                c.yview_moveto(max(0, (y1 - vis_h / 2) / alto))
