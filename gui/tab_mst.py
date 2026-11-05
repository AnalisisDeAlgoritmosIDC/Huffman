"""
Pestaña de la GUI para el Árbol de Expansión Mínima (Kruskal y Prim)
con animación paso a paso.
"""
import time
import tkinter as tk
from tkinter import ttk

from mst import generar_grafo_aleatorio, kruskal, prim, etiqueta
from . import estilos as E

ANCHO_BASE, ALTO_BASE = 700, 480   # sistema de coordenadas del generador


class PestanaMST(ttk.Frame):
    def __init__(self, master, estado):
        super().__init__(master)
        self.estado = estado
        self.grafo = None
        self.pasos = []
        self.paso_actual = 0
        self.animando = False
        self.resultado = None

        self.var_nodos = tk.IntVar(value=12)
        self.var_densidad = tk.DoubleVar(value=0.4)
        self.var_semilla = tk.StringVar(value="7")
        self.var_algoritmo = tk.StringVar(value="Kruskal")
        self.var_inicio = tk.StringVar(value="A")
        self.var_velocidad = tk.IntVar(value=500)

        self._crear_controles()
        self._crear_lienzo()
        self._crear_bitacora()
        self.generar()

    # ================================================================ interfaz
    def _crear_controles(self):
        panel = ttk.Frame(self, padding=(12, 12, 6, 12))
        panel.pack(side="left", fill="y")

        g = ttk.Labelframe(panel, text="Grafo", padding=8)
        g.pack(fill="x")
        ttk.Label(g, text="Nodos").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(g, from_=3, to=40, textvariable=self.var_nodos, width=6).grid(row=0, column=1, sticky="e")
        ttk.Label(g, text="Densidad").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Scale(g, from_=0.1, to=1.0, variable=self.var_densidad).grid(row=1, column=1, sticky="ew")
        ttk.Label(g, text="Semilla").grid(row=2, column=0, sticky="w")
        ttk.Entry(g, textvariable=self.var_semilla, width=8).grid(row=2, column=1, sticky="e")
        ttk.Button(g, text="Generar grafo", command=self.generar).grid(row=3, column=0, columnspan=2,
                                                                      sticky="ew", pady=(10, 0))
        g.columnconfigure(1, weight=1)

        a = ttk.Labelframe(panel, text="Algoritmo", padding=8)
        a.pack(fill="x", pady=6)
        for nombre in ("Kruskal", "Prim"):
            ttk.Radiobutton(a, text=nombre, value=nombre, variable=self.var_algoritmo,
                            command=self.reiniciar).pack(anchor="w")
        fila = ttk.Frame(a)
        fila.pack(fill="x", pady=(6, 0))
        ttk.Label(fila, text="Inicio (Prim)").pack(side="left")
        self.combo_inicio = ttk.Combobox(fila, textvariable=self.var_inicio, width=5, state="readonly")
        self.combo_inicio.pack(side="right")
        self.combo_inicio.bind("<<ComboboxSelected>>", lambda e: self.reiniciar())

        ttk.Button(a, text="Ejecutar completo", style="Acento.TButton",
                   command=self.ejecutar_completo).pack(fill="x", pady=(10, 4))
        ttk.Button(a, text="Siguiente paso", command=self.siguiente_paso).pack(fill="x")
        self.btn_animar = ttk.Button(a, text="▶ Animar", command=self.alternar_animacion)
        self.btn_animar.pack(fill="x", pady=4)
        ttk.Button(a, text="Reiniciar", command=self.reiniciar).pack(fill="x")
        ttk.Label(a, text="Velocidad (ms por paso)").pack(anchor="w", pady=(4, 0))
        ttk.Scale(a, from_=100, to=1500, variable=self.var_velocidad).pack(fill="x")

        r = ttk.Labelframe(panel, text="Resultado", padding=8)
        r.pack(fill="x")
        self.lbl_peso = ttk.Label(r, text="—", font=E.fuente(18, "bold"), foreground=E.VERDE)
        self.lbl_peso.pack(anchor="w")
        ttk.Label(r, text="peso total del árbol", foreground=E.TINTA_SUAVE).pack(anchor="w")
        self.lbl_detalle = ttk.Label(r, text="", justify="left", wraplength=240)
        self.lbl_detalle.pack(anchor="w", pady=(4, 0))

    def _crear_lienzo(self):
        marco = ttk.Frame(self, padding=(6, 12, 6, 12))
        marco.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(marco, bg=E.PANEL, highlightthickness=1, highlightbackground=E.GRIS)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.dibujar())
        leyenda = ttk.Frame(marco)
        leyenda.pack(fill="x", pady=(6, 0))
        for color, texto in ((E.VERDE, "en el árbol"), (E.ACENTO, "evaluando"),
                             (E.ROJO, "rechazada (ciclo / ya visitado)"), (E.GRIS, "sin evaluar")):
            muestra = tk.Canvas(leyenda, width=22, height=10, bg=E.FONDO, highlightthickness=0)
            muestra.create_line(2, 5, 20, 5, fill=color, width=4)
            muestra.pack(side="left")
            ttk.Label(leyenda, text=texto, foreground=E.TINTA_SUAVE).pack(side="left", padx=(2, 14))

    def _crear_bitacora(self):
        marco = ttk.Labelframe(self, text="Bitácora de pasos", padding=6)
        marco.pack(side="right", fill="y", padx=(6, 12), pady=12)
        self.bitacora = ttk.Treeview(marco, columns=("n", "arista", "peso", "decision"),
                                     show="headings", height=20)
        for col, titulo, ancho in (("n", "#", 36), ("arista", "Arista", 70),
                                   ("peso", "Peso", 50), ("decision", "Decisión", 135)):
            self.bitacora.heading(col, text=titulo)
            self.bitacora.column(col, width=ancho, anchor="center" if col != "decision" else "w")
        self.bitacora.tag_configure("si", foreground=E.VERDE)
        self.bitacora.tag_configure("no", foreground=E.ROJO)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.bitacora.yview)
        self.bitacora.configure(yscrollcommand=sy.set)
        self.bitacora.pack(side="left", fill="y")
        sy.pack(side="right", fill="y")

    # ================================================================ lógica
    def generar(self):
        try:
            semilla = int(self.var_semilla.get())
        except ValueError:
            semilla = None
        n = max(3, min(40, int(self.var_nodos.get())))
        self.grafo = generar_grafo_aleatorio(n, self.var_densidad.get(), semilla, ANCHO_BASE, ALTO_BASE)
        etiquetas = [etiqueta(i) for i in range(n)]
        self.combo_inicio.configure(values=etiquetas)
        if self.var_inicio.get() not in etiquetas:
            self.var_inicio.set("A")
        self.estado.set("Grafo generado: %d nodos, %d aristas." % (n, len(self.grafo.aristas)))
        self.reiniciar()

    def _inicio(self):
        etiquetas = list(self.combo_inicio.cget("values"))
        valor = self.var_inicio.get()
        return etiquetas.index(valor) if valor in etiquetas else 0

    def reiniciar(self):
        self.detener_animacion()
        g = self.grafo
        t0 = time.perf_counter()
        if self.var_algoritmo.get() == "Kruskal":
            arbol, total, self.pasos = kruskal(g)
        else:
            arbol, total, self.pasos = prim(g, self._inicio())
        tiempo = time.perf_counter() - t0
        self.resultado = (arbol, total, tiempo)
        self.paso_actual = 0
        self.bitacora.delete(*self.bitacora.get_children())
        self.lbl_peso.configure(text="—")
        self.lbl_detalle.configure(text="")
        self.dibujar()

    def siguiente_paso(self):
        if self.paso_actual >= len(self.pasos):
            self.detener_animacion()
            return False
        peso, u, v, aceptada = self.pasos[self.paso_actual]
        self.paso_actual += 1
        if aceptada:
            decision = "✔ se agrega"
        elif self.var_algoritmo.get() == "Kruskal":
            decision = "✘ formaría ciclo"
        else:
            decision = "✘ ya visitado"
        item = self.bitacora.insert("", "end", tags=("si" if aceptada else "no",),
                                    values=(self.paso_actual, "%s–%s" % (etiqueta(u), etiqueta(v)),
                                            peso, decision))
        self.bitacora.see(item)
        acumulado = sum(p for p, _, _, ok in self.pasos[:self.paso_actual] if ok)
        self.lbl_peso.configure(text=str(acumulado))
        if self.paso_actual == len(self.pasos):
            self._mostrar_resumen()
        self.dibujar()
        return True

    def ejecutar_completo(self):
        self.detener_animacion()
        while self.siguiente_paso():
            pass

    def alternar_animacion(self):
        if self.animando:
            self.detener_animacion()
        else:
            if self.paso_actual >= len(self.pasos):
                self.reiniciar()
            self.animando = True
            self.btn_animar.configure(text="⏸ Pausar")
            self._tic()

    def _tic(self):
        if self.animando and self.siguiente_paso():
            self.after(int(self.var_velocidad.get()), self._tic)
        else:
            self.detener_animacion()

    def detener_animacion(self):
        self.animando = False
        if hasattr(self, "btn_animar"):
            self.btn_animar.configure(text="▶ Animar")

    def _mostrar_resumen(self):
        arbol, total, tiempo = self.resultado
        # Comparación con el otro algoritmo: ambos deben dar el mismo peso
        if self.var_algoritmo.get() == "Kruskal":
            otro_nombre, otro_total = "Prim", prim(self.grafo)[1]
        else:
            otro_nombre, otro_total = "Kruskal", kruskal(self.grafo)[1]
        rechazadas = sum(1 for p in self.pasos if not p[3])
        self.lbl_peso.configure(text=str(total))
        self.lbl_detalle.configure(text=(
            "%d aristas en el árbol (n − 1)\n%d evaluadas · %d rechazadas\n"
            "Tiempo: %.3f ms\n%s: peso %d → %s" % (
                len(arbol), len(self.pasos), rechazadas, tiempo * 1000, otro_nombre, otro_total,
                "coinciden ✔" if otro_total == total else "¡difieren!")))
        self.estado.set("%s terminado: peso mínimo %d con %d aristas." %
                        (self.var_algoritmo.get(), total, len(arbol)))

    # ================================================================ dibujo
    def dibujar(self):
        c = self.canvas
        c.delete("all")
        if self.grafo is None:
            return
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50:
            return
        esc = min(ancho / ANCHO_BASE, alto / ALTO_BASE)
        dx, dy = (ancho - ANCHO_BASE * esc) / 2, (alto - ALTO_BASE * esc) / 2

        def p(n):
            x, y = self.grafo.posiciones[n]
            return dx + x * esc, dy + y * esc

        hechos = self.pasos[:self.paso_actual]
        aceptadas = {(min(u, v), max(u, v)) for _, u, v, ok in hechos if ok}
        rechazadas = {(min(u, v), max(u, v)) for _, u, v, ok in hechos if not ok}
        actual = None
        if hechos and self.paso_actual < len(self.pasos):
            _, u, v, _ = hechos[-1]
            actual = (min(u, v), max(u, v))
        visitados = set()
        if self.var_algoritmo.get() == "Prim" and self.paso_actual:
            visitados.add(self._inicio())
        for _, u, v, ok in hechos:
            if ok:
                visitados.update((u, v))

        # Aristas: primero las grises, luego las coloreadas encima
        orden = sorted(self.grafo.aristas, key=lambda a: (min(a[1], a[2]), max(a[1], a[2])) in aceptadas)
        for peso, u, v in orden:
            clave = (min(u, v), max(u, v))
            x1, y1 = p(u)
            x2, y2 = p(v)
            if clave == actual:
                color, grosor, guiones = E.ACENTO, 5, None
            elif clave in aceptadas:
                color, grosor, guiones = E.VERDE, 4, None
            elif clave in rechazadas:
                color, grosor, guiones = E.ROJO, 1.5, (4, 3)
            else:
                color, grosor, guiones = E.GRIS, 1.5, None
            c.create_line(x1, y1, x2, y2, fill=color, width=grosor, dash=guiones)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            c.create_rectangle(mx - 11, my - 8, mx + 11, my + 8, fill=E.PANEL, outline="")
            c.create_text(mx, my, text=str(peso), font=E.fuente(8, "bold" if clave in aceptadas else "normal"),
                          fill=color if color != E.GRIS else E.TINTA_SUAVE)

        radio = max(11, 15 * esc)
        for n in range(self.grafo.num_nodos):
            x, y = p(n)
            relleno = E.VERDE if n in visitados else E.TINTA
            c.create_oval(x - radio, y - radio, x + radio, y + radio, fill=relleno, outline="white", width=2)
            c.create_text(x, y, text=etiqueta(n), fill="white", font=E.fuente(10, "bold"))
