"""
Pestaña de la GUI para comprimir y descomprimir archivos con Huffman.
"""
import math
import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from huffman import (
    leer_texto, calcular_frecuencias, ordenar_frecuencias, describir_caracter,
    construir_arbol, altura, contar_nodos, generar_codigos, codificar,
    guardar_comprimido, descomprimir_archivo, longitud_promedio, entropia,
    comparar_tamanos, formatear_bytes,
)
from .vista_arbol import VistaArbol
from . import estilos as E

LIMITE_VISTA = 6000   # caracteres que se muestran en las vistas de texto


class PestanaHuffman(ttk.Frame):
    def __init__(self, master, estado):
        super().__init__(master)
        self.estado = estado                # StringVar de la barra de estado
        self.ruta_txt = None
        self.ruta_huf = None
        self.texto = ""
        self.codificacion = "utf-8"
        self.frecuencias = {}
        self.raiz = None
        self.pasos = []
        self.codigos = {}
        self.bits = ""
        self.resultados = {}

        self._crear_barra()
        self._crear_cuerpo()

    # ================================================================ interfaz
    def _crear_barra(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=12, pady=(12, 6))
        ttk.Button(barra, text="1 · Abrir archivo .txt", style="Acento.TButton",
                   command=self.accion_abrir).pack(side="left")
        self.btn_codificar = ttk.Button(barra, text="2 · Codificar y guardar .huf",
                                        command=self.accion_codificar, state="disabled")
        self.btn_codificar.pack(side="left", padx=6)
        ttk.Button(barra, text="3 · Decodificar .huf → .txt",
                   command=self.accion_decodificar).pack(side="left")
        self.lbl_archivo = ttk.Label(barra, text="Ningún archivo cargado", foreground=E.TINTA_SUAVE)
        self.lbl_archivo.pack(side="right")

    def _crear_cuerpo(self):
        panel = ttk.PanedWindow(self, orient="horizontal")
        panel.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # ---------- Izquierda: tabla de frecuencias y códigos
        izq = ttk.Labelframe(panel, text="Frecuencias y códigos de Huffman", padding=6)
        columnas = ("car", "frec", "prob", "codigo", "bits")
        self.tabla = ttk.Treeview(izq, columns=columnas, show="headings", selectmode="browse")
        encabezados = {"car": ("Carácter", 100), "frec": ("Frecuencia", 95), "prob": ("Prob.", 62),
                       "codigo": ("Código", 140), "bits": ("Bits", 42)}
        for col, (titulo, ancho) in encabezados.items():
            self.tabla.heading(col, text=titulo, command=lambda c=col: self._ordenar_tabla(c))
            self.tabla.column(col, width=ancho, anchor="w" if col in ("car", "codigo") else "e",
                              stretch=col == "codigo")
        self.tabla.tag_configure("par", background="#faf8f3")
        sy = ttk.Scrollbar(izq, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sy.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        self.lbl_resumen = ttk.Label(izq, text="", foreground=E.TINTA_SUAVE)
        self.lbl_resumen.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        izq.rowconfigure(0, weight=1)
        izq.columnconfigure(0, weight=1)
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)
        panel.add(izq, weight=2)

        # ---------- Derecha: pestañas internas
        der = ttk.Notebook(panel)
        panel.add(der, weight=5)

        self.vista_arbol = VistaArbol(der)
        der.add(self.vista_arbol, text="Árbol de Huffman")

        marco_pasos = ttk.Frame(der, style="Panel.TFrame", padding=8)
        ttk.Label(marco_pasos, text="Cada paso une los dos nodos de MENOR frecuencia (elección voraz).",
                  style="Dato.TLabel").pack(anchor="w", pady=(0, 6))
        self.tabla_pasos = ttk.Treeview(marco_pasos, columns=("n", "a", "b", "suma"), show="headings")
        for col, titulo, ancho in (("n", "Paso", 60), ("a", "Nodo menor", 220),
                                   ("b", "Segundo menor", 220), ("suma", "Nuevo nodo", 120)):
            self.tabla_pasos.heading(col, text=titulo)
            self.tabla_pasos.column(col, width=ancho, anchor="w")
        sp = ttk.Scrollbar(marco_pasos, orient="vertical", command=self.tabla_pasos.yview)
        self.tabla_pasos.configure(yscrollcommand=sp.set)
        self.tabla_pasos.pack(side="left", fill="both", expand=True)
        sp.pack(side="right", fill="y")
        der.add(marco_pasos, text="Pasos voraces")

        marco_texto = ttk.Frame(der, style="Panel.TFrame", padding=8)
        self.txt_original = self._caja_texto(marco_texto, "Texto original", 0)
        self.txt_bits = self._caja_texto(marco_texto, "Texto codificado (bits)", 1)
        self.txt_decodificado = self._caja_texto(marco_texto, "Texto decodificado", 2)
        marco_texto.columnconfigure((0, 1, 2), weight=1)
        marco_texto.rowconfigure(1, weight=1)
        der.add(marco_texto, text="Texto")

        self.marco_resultados = ttk.Frame(der, style="Panel.TFrame", padding=16)
        der.add(self.marco_resultados, text="Resultados de compresión")
        self._crear_resultados()
        self.notebook = der
        # Ancho inicial del panel izquierdo para que se vean todas las columnas
        self.after(100, lambda: panel.sashpos(0, 470))

    def _caja_texto(self, padre, titulo, columna):
        ttk.Label(padre, text=titulo, style="Valor.TLabel").grid(row=0, column=columna, sticky="w", padx=4)
        caja = tk.Text(padre, wrap="word", font=E.fuente_mono(9), bg="#fbfaf7", relief="flat",
                       padx=8, pady=8, highlightthickness=1, highlightbackground=E.GRIS)
        caja.grid(row=1, column=columna, sticky="nsew", padx=4, pady=4)
        caja.configure(state="disabled")
        return caja

    def _crear_resultados(self):
        m = self.marco_resultados
        izquierda = ttk.Frame(m, style="Panel.TFrame")
        izquierda.pack(side="left", fill="y", padx=(0, 20))
        self.lbl_ahorro = ttk.Label(izquierda, text="—", style="Grande.TLabel")
        self.lbl_ahorro.pack(anchor="w")
        ttk.Label(izquierda, text="de espacio ahorrado", style="Dato.TLabel").pack(anchor="w", pady=(0, 12))

        self.valores = {}
        filas = [
            ("original", "Tamaño original (.txt)"),
            ("datos", "Bits codificados (solo datos)"),
            ("huf", "Archivo .huf (datos + tabla)"),
            ("razon", "Razón de compresión"),
            ("prom", "Bits promedio por carácter"),
            ("fijo", "Bits por carácter sin comprimir"),
            ("entropia", "Entropía de Shannon"),
            ("eficiencia", "Eficiencia del código (H / L)"),
            ("arbol", "Árbol: hojas · nodos · altura"),
            ("t_cod", "Tiempo de codificación"),
            ("t_dec", "Tiempo de decodificación"),
            ("verif", "Verificación decodificado = original"),
        ]
        tabla = ttk.Frame(izquierda, style="Panel.TFrame")
        tabla.pack(anchor="w")
        for i, (clave, texto) in enumerate(filas):
            ttk.Label(tabla, text=texto, style="Dato.TLabel").grid(row=i, column=0, sticky="w", pady=3)
            valor = ttk.Label(tabla, text="—", style="Valor.TLabel")
            valor.grid(row=i, column=1, sticky="e", padx=(24, 0), pady=3)
            self.valores[clave] = valor

        self.grafica = tk.Canvas(m, bg=E.PANEL, highlightthickness=0)
        self.grafica.pack(side="left", fill="both", expand=True)
        self.grafica.bind("<Configure>", lambda e: self._dibujar_grafica())

    # ================================================================ acciones
    def accion_abrir(self):
        ruta = filedialog.askopenfilename(title="Selecciona un libro en .txt",
                                          filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if ruta:
            self.cargar_archivo(ruta)

    def accion_codificar(self):
        if not self.texto:
            return
        sugerido = os.path.splitext(os.path.basename(self.ruta_txt))[0] + ".huf"
        ruta = filedialog.asksaveasfilename(title="Guardar archivo comprimido", defaultextension=".huf",
                                            initialfile=sugerido, initialdir=os.path.dirname(self.ruta_txt),
                                            filetypes=[("Huffman", "*.huf")])
        if ruta:
            self.codificar_y_guardar(ruta)

    def accion_decodificar(self):
        ruta_huf = filedialog.askopenfilename(title="Selecciona el archivo .huf",
                                              initialfile=os.path.basename(self.ruta_huf or ""),
                                              initialdir=os.path.dirname(self.ruta_huf or self.ruta_txt or "."),
                                              filetypes=[("Huffman", "*.huf"), ("Todos", "*.*")])
        if not ruta_huf:
            return
        sugerido = os.path.splitext(os.path.basename(ruta_huf))[0] + "_decodificado.txt"
        ruta_txt = filedialog.asksaveasfilename(title="Guardar texto decodificado", defaultextension=".txt",
                                                initialfile=sugerido, initialdir=os.path.dirname(ruta_huf),
                                                filetypes=[("Texto", "*.txt")])
        if ruta_txt:
            self.decodificar(ruta_huf, ruta_txt)

    # ================================================================ lógica
    def cargar_archivo(self, ruta):
        """Lee el .txt, calcula frecuencias, construye el árbol y los códigos."""
        try:
            self.texto, self.codificacion = leer_texto(ruta)
        except OSError as error:
            messagebox.showerror("Error", "No se pudo leer el archivo:\n%s" % error)
            return
        self.ruta_txt = ruta
        self.frecuencias = calcular_frecuencias(self.texto)
        self.raiz, self.pasos = construir_arbol(self.frecuencias)
        self.codigos = generar_codigos(self.raiz)
        self.bits = ""
        self.resultados = {"original": os.path.getsize(ruta)}

        self._llenar_tabla()
        self._llenar_pasos()
        self.vista_arbol.dibujar(self.raiz)
        self._poner_texto(self.txt_original, self.texto)
        self._poner_texto(self.txt_bits, "")
        self._poner_texto(self.txt_decodificado, "")
        self._actualizar_resultados()

        nombre = os.path.basename(ruta)
        self.lbl_archivo.configure(text="%s · %s · %s" % (nombre, formatear_bytes(self.resultados["original"]),
                                                         self.codificacion))
        self.lbl_resumen.configure(text="%d caracteres en total · %d distintos" %
                                   (len(self.texto), len(self.frecuencias)))
        self.btn_codificar.configure(state="normal" if self.texto else "disabled")
        self.estado.set("Archivo cargado: %s. Árbol construido con %d uniones voraces." %
                        (nombre, len(self.pasos)))

    def codificar_y_guardar(self, ruta_huf):
        inicio = time.perf_counter()
        self.bits = codificar(self.texto, self.codigos)
        tam_huf = guardar_comprimido(ruta_huf, self.frecuencias, self.bits, self.codificacion)
        self.resultados["t_cod"] = time.perf_counter() - inicio
        self.resultados["datos"] = math.ceil(len(self.bits) / 8)
        self.resultados["huf"] = tam_huf
        self.ruta_huf = ruta_huf

        self._poner_texto(self.txt_bits, self._agrupar_bits(self.bits[:LIMITE_VISTA * 2]))
        self._actualizar_resultados()
        self.notebook.select(self.marco_resultados)
        self.estado.set("Codificado: %s bits → %s (%s)" % (format(len(self.bits), ","),
                                                         os.path.basename(ruta_huf), formatear_bytes(tam_huf)))

    def decodificar(self, ruta_huf, ruta_salida):
        try:
            inicio = time.perf_counter()
            texto = descomprimir_archivo(ruta_huf, ruta_salida)
            self.resultados["t_dec"] = time.perf_counter() - inicio
        except (OSError, ValueError) as error:
            messagebox.showerror("Error", "No se pudo decodificar:\n%s" % error)
            return
        self._poner_texto(self.txt_decodificado, texto)
        if self.ruta_txt:
            with open(self.ruta_txt, "rb") as a, open(ruta_salida, "rb") as b:
                self.resultados["verif"] = a.read() == b.read()
        self._actualizar_resultados()
        self.estado.set("Decodificado %s → %s" % (os.path.basename(ruta_huf), os.path.basename(ruta_salida)))

    # ================================================================ helpers
    def _llenar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        total = len(self.texto) or 1
        for i, (car, frec) in enumerate(ordenar_frecuencias(self.frecuencias)):
            codigo = self.codigos[car]
            self.tabla.insert("", "end", iid=str(ord(car)), tags=("par",) if i % 2 else (),
                              values=(describir_caracter(car), frec, "%.4f" % (frec / total),
                                      codigo, len(codigo)))

    def _ordenar_tabla(self, columna):
        filas = [(self.tabla.set(i, columna), i) for i in self.tabla.get_children("")]
        numerica = columna in ("frec", "prob", "bits")
        descendente = getattr(self, "_orden_desc", {}).get(columna, numerica)
        filas.sort(key=lambda f: float(f[0]) if numerica else f[0], reverse=descendente)
        for posicion, (_, iid) in enumerate(filas):
            self.tabla.move(iid, "", posicion)
        self._orden_desc = {columna: not descendente}

    def _al_seleccionar(self, _evento):
        seleccion = self.tabla.selection()
        if seleccion:
            caracter = chr(int(seleccion[0]))
            self.vista_arbol.resaltar(self.codigos.get(caracter, ""))

    def _llenar_pasos(self):
        self.tabla_pasos.delete(*self.tabla_pasos.get_children())

        def nombre(n):
            if n.es_hoja():
                return "'%s'  (%d)" % (describir_caracter(n.caracter), n.frecuencia)
            return "nodo interno  (%d)" % n.frecuencia

        for i, (a, b, padre) in enumerate(self.pasos, 1):
            self.tabla_pasos.insert("", "end", values=(i, nombre(a), nombre(b), padre.frecuencia))

    @staticmethod
    def _agrupar_bits(bits):
        return " ".join(bits[i:i + 8] for i in range(0, len(bits), 8))

    @staticmethod
    def _poner_texto(caja, contenido):
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        if len(contenido) > LIMITE_VISTA:
            contenido = contenido[:LIMITE_VISTA] + "\n\n[... vista recortada, %s caracteres en total ...]" % \
                format(len(contenido), ",")
        caja.insert("1.0", contenido)
        caja.configure(state="disabled")

    def _actualizar_resultados(self):
        r = self.resultados
        v = self.valores
        guion = "—"
        v["original"].configure(text=formatear_bytes(r["original"]) + "  (%s B)" % format(r["original"], ",")
                                if "original" in r else guion)
        v["datos"].configure(text=formatear_bytes(r["datos"]) if "datos" in r else guion)
        v["huf"].configure(text=formatear_bytes(r["huf"]) + "  (%s B)" % format(r["huf"], ",")
                           if "huf" in r else guion)
        if "huf" in r:
            comp = comparar_tamanos(r["original"], r["huf"])
            v["razon"].configure(text="%.3f : 1" % comp["razon"])
            self.lbl_ahorro.configure(text="%.2f %%" % comp["ahorro"])
        else:
            v["razon"].configure(text=guion)
            self.lbl_ahorro.configure(text=guion)
        if self.frecuencias:
            l = longitud_promedio(self.frecuencias, self.codigos)
            h = entropia(self.frecuencias)
            fijo = r["original"] * 8 / max(1, len(self.texto))
            v["prom"].configure(text="%.4f bits" % l)
            v["fijo"].configure(text="%.2f bits" % fijo)
            v["entropia"].configure(text="%.4f bits" % h)
            v["eficiencia"].configure(text="%.2f %%" % (h / l * 100 if l else 0))
            v["arbol"].configure(text="%d · %d · %d" % (len(self.frecuencias), contar_nodos(self.raiz),
                                                        altura(self.raiz)))
        v["t_cod"].configure(text="%.3f s" % r["t_cod"] if "t_cod" in r else guion)
        v["t_dec"].configure(text="%.3f s" % r["t_dec"] if "t_dec" in r else guion)
        if "verif" in r:
            v["verif"].configure(text="✔ idénticos" if r["verif"] else "✘ difieren",
                                 foreground=E.VERDE if r["verif"] else E.ROJO)
        else:
            v["verif"].configure(text=guion, foreground=E.TINTA)
        self._dibujar_grafica()

    def _dibujar_grafica(self):
        c = self.grafica
        c.delete("all")
        r = self.resultados
        if "original" not in r:
            return
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50:
            return
        barras = [("Original", r["original"], E.TINTA)]
        if "huf" in r:
            barras.append(("Comprimido .huf", r["huf"], E.ACENTO))
            barras.append(("Solo datos", r["datos"], E.HOJA))
        c.create_text(20, 20, text="Comparación de tamaños", anchor="w", font=E.fuente(12, "bold"), fill=E.TINTA)
        maximo = max(b[1] for b in barras) or 1
        base, techo = alto - 50, 60
        ancho_barra = min(110, (ancho - 60) / (len(barras) * 1.6))
        for i, (nombre, valor, color) in enumerate(barras):
            x = 40 + i * ancho_barra * 1.6
            h = (base - techo) * valor / maximo
            c.create_rectangle(x, base - h, x + ancho_barra, base, fill=color, outline="")
            c.create_text(x + ancho_barra / 2, base - h - 12, text=formatear_bytes(valor),
                          font=E.fuente(10, "bold"), fill=E.TINTA)
            c.create_text(x + ancho_barra / 2, base + 16, text=nombre, font=E.fuente(9), fill=E.TINTA_SUAVE)
        c.create_line(30, base, ancho - 20, base, fill=E.GRIS)
