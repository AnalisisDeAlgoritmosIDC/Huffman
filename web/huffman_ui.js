// Pestaña de Huffman: muestra los resultados que calcula puente.py.

import { CARPETA, py, escribir, leer, borrar, ocupado, formatoBytes, miles, descargar, escaparHTML, aviso } from "./python.js";
import { dibujarJerarquico, dibujarExplorador, arrastrable } from "./arbol.js";
import { dibujarRadial } from "./arbol_radial.js";
import { montarConstruccion, detener as detenerConstruccion } from "./construccion.js";
import { montarAhorro, actualizarAhorro } from "./ahorro.js";
import { montarIdioma } from "./idioma_ui.js";

const $ = (id) => document.getElementById(id);
const RUTA_TXT = CARPETA + "/original.txt";
const RUTA_HUF = CARPETA + "/comprimido.mc";
const RUTA_DEC = CARPETA + "/decodificado.txt";
const LIMITE_BITS_VISTA = 4000;

let datos = null;   // resultado de analizar()
let comp = null;    // resultado de comprimir()
let dec = null;     // resultado de descomprimir()
let nombreBase = "libro";
let vista = "jerarquico";
let vistaActual = null;
let escala = 1;
let seleccion = "";
let bitsCompletos = "";

export function iniciarHuffman() {
  $("btn-codificar").addEventListener("click", codificar);
  $("btn-decodificar").addEventListener("click", decodificar);
  $("btn-bajar-huf").addEventListener("click", () =>
    descargar(leer(RUTA_HUF), nombreBase + ".mc", "application/octet-stream"));
  $("btn-bajar-txt").addEventListener("click", () =>
    descargar(leer(RUTA_DEC), nombreBase + "_decodificado.txt", "text/plain"));
  $("btn-copiar").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(bitsCompletos);
      aviso("Bits copiados al portapapeles (primeros " + miles(bitsCompletos.length) + ").", "ok");
    } catch (e) {
      aviso("No se pudo copiar al portapapeles.", "error");
    }
  });
  $("zoom-mas").addEventListener("click", () => cambiarZoom(1.25));
  $("zoom-menos").addEventListener("click", () => cambiarZoom(0.8));
  $("zoom-centrar").addEventListener("click", () => { escala = 1; dibujar(); });
  arrastrable($("lienzo-arbol"));

  $("selector-vista").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-vista]");
    if (!b) return;
    vista = b.dataset.vista;
    $("selector-vista").querySelectorAll("button").forEach((x) => x.classList.toggle("activo", x === b));
    escala = 1;
    dibujar();
  });

  document.querySelectorAll(".pestana").forEach((b) =>
    b.addEventListener("click", () => mostrarSub(b.dataset.sub)));

  $("tabla-codigos").addEventListener("click", (e) => {
    const fila = e.target.closest("tr[data-codigo]");
    if (!fila) return;
    seleccion = fila.dataset.codigo;
    document.querySelectorAll("#tabla-codigos tr.sel").forEach((f) => f.classList.remove("sel"));
    fila.classList.add("sel");
    if (vista === "construccion") seleccionarVista("jerarquico");
    mostrarSub("sub-arbol");
    vistaActual?.resaltar(seleccion);
  });

  $("filtro-tabla").addEventListener("input", (e) => {
    const termino = e.target.value.toLowerCase();
    document.querySelectorAll("#tabla-codigos tbody tr").forEach((fila) => {
      fila.style.display = fila.textContent.toLowerCase().includes(termino) ? "" : "none";
    });
  });
}

function seleccionarVista(nombre) {
  vista = nombre;
  $("selector-vista").querySelectorAll("button").forEach((x) => x.classList.toggle("activo", x.dataset.vista === nombre));
  dibujar();
}

function mostrarSub(id) {
  document.querySelectorAll(".pestana").forEach((b) => b.classList.toggle("activa", b.dataset.sub === id));
  document.querySelectorAll(".subpanel").forEach((p) => p.classList.toggle("activo", p.id === id));
  if (id === "sub-arbol" && datos && !vistaActual) dibujar();
  if (id !== "sub-arbol") detenerConstruccion();
}

/** Recibe los bytes del libro (de Gutenberg o subido) y lo analiza en Python. */
export async function cargarLibro(bytes, titulo, detalle, nombreArchivo) {
  nombreBase = (nombreArchivo || titulo).replace(/\.[^.]+$/, "").replace(/[^\w\-]+/g, "_").slice(0, 60) || "libro";
  await ocupado("Contando frecuencias, construyendo el árbol y detectando el idioma…", () => {
    borrar(RUTA_HUF);
    borrar(RUTA_DEC);
    escribir(RUTA_TXT, bytes);
    datos = py("analizar()");
  });
  comp = dec = null;
  bitsCompletos = "";
  vistaActual = null;
  seleccion = "";
  escala = 1;

  $("vacio").classList.add("oculto");
  $("libro-titulo").textContent = titulo;
  $("libro-detalle").textContent = [detalle, formatoBytes(datos.original), miles(datos.caracteres) + " caracteres",
    datos.distintos + " distintos", datos.codificacion].filter(Boolean).join(" · ");
  $("btn-codificar").disabled = false;
  $("btn-decodificar").disabled = true;
  $("btn-bajar-huf").disabled = true;
  $("btn-bajar-txt").disabled = true;
  $("btn-copiar").disabled = true;
  estado("ÁRBOL CONSTRUIDO");

  llenarTabla();
  $("txt-original").textContent = recorte(datos.muestra, datos.caracteres);
  $("txt-bits").innerHTML = '<span class="tenue cursiva">Presiona CODIFICAR para ver la cadena de bits…</span>';
  $("txt-decodificado").innerHTML = '<span class="tenue cursiva">El texto reconstruido aparecerá aquí…</span>';
  montarAhorro($("ahorro"), datos, null);
  montarIdioma($("idioma-detalle"), datos.idioma);
  actualizarMetricas();
  mostrarSub("sub-arbol");
  dibujar();
  aviso(`Libro analizado: ${datos.distintos} caracteres distintos · idioma ${datos.idioma.nombre}.`, "ok");
  if (datos.original > 2 * 1024 * 1024) aviso("Libro grande: codificar y decodificar puede tardar unos segundos.");
}

async function codificar() {
  await ocupado("Codificando y escribiendo el archivo .mc…", () => { comp = py("comprimir()"); });
  dec = null;
  bitsCompletos = comp.muestra_bits;
  const muestra = comp.muestra_bits.slice(0, LIMITE_BITS_VISTA);
  let html = "";
  for (let i = 0; i < muestra.length; i += 8) {
    html += [...muestra.slice(i, i + 8)].map((b) => `<span class="${b === "0" ? "c" : "u"}">${b}</span>`).join("") + " ";
  }
  if (comp.bits > muestra.length) html += `<span class="tenue"> … ${miles(comp.bits)} bits en total</span>`;
  $("txt-bits").innerHTML = html;
  $("txt-decodificado").innerHTML = '<span class="tenue cursiva">Presiona DECODIFICAR para reconstruir el texto…</span>';
  $("btn-decodificar").disabled = false;
  $("btn-bajar-huf").disabled = false;
  $("btn-bajar-txt").disabled = true;
  $("btn-copiar").disabled = false;
  estado("CODIFICADO");
  actualizarMetricas();
  actualizarAhorro(comp);
  aviso(`Codificado: ${formatoBytes(datos.original)} → ${formatoBytes(comp.huf)} (${comp.ahorro.toFixed(2)} % menos).`, "ok");
}

async function decodificar() {
  await ocupado("Leyendo el .mc y decodificando bit por bit…", () => { dec = py("descomprimir()"); });
  $("txt-decodificado").textContent = recorte(dec.muestra, dec.caracteres);
  $("btn-bajar-txt").disabled = false;
  estado(dec.identico === false ? "DIFERENCIAS" : "VERIFICADO");
  actualizarMetricas();
  mostrarSub("sub-bits");
  if (dec.identico) aviso("¡Decodificación exitosa! El archivo es idéntico al original byte por byte.", "ok");
  else if (dec.identico === false) aviso("El archivo decodificado no coincide con el original.", "error");
}

/** Decodifica un .mc subido por el usuario y luego lo carga como libro. */
export async function decodificarArchivoHuf(bytes, nombre) {
  await ocupado("Decodificando " + nombre + "…", () => {
    borrar(RUTA_TXT);
    escribir(RUTA_HUF, bytes);
    py("descomprimir()");
  });
  const texto = leer(RUTA_DEC);
  await cargarLibro(texto, nombre + " (decodificado)", "decodificado de un .mc", nombre);
  await codificar();
  await decodificar();
}

// ------------------------------------------------------------------ vistas
function estado(texto) {
  $("insignia-estado").innerHTML = `<i class="punto"></i>${texto}`;
}

function llenarTabla() {
  $("simbolos").textContent = `Símbolos únicos: ${datos.distintos}`;
  const especiales = /^(␣|\\n|\\r|\\t|BOM|U\+)/;
  const crudos = Object.entries(datos.codigos_crudos);
  const porCodigo = new Map(crudos.map(([c, cod]) => [cod, c]));
  const filas = datos.tabla.map((f) => {
    const crudo = porCodigo.get(f.codigo) ?? "";
    const punto = crudo ? "U+" + crudo.codePointAt(0).toString(16).toUpperCase().padStart(4, "0") : "";
    const car = especiales.test(f.car) ? `<span class="car-especial">${escaparHTML(f.car)}</span>` : `<b>${escaparHTML(f.car)}</b>`;
    const pct = f.prob * 100;
    return `<tr data-codigo="${f.codigo}"><td>${car}</td><td class="tenue">${punto}</td><td class="num fucsia">${miles(f.frec)}</td>` +
      `<td>${pct.toFixed(2)} %<span class="mini-barra"><i style="width:${Math.min(100, pct * 4)}%"></i></span></td>` +
      `<td class="codigo">${f.codigo}</td><td class="num tenue">${f.codigo.length}</td></tr>`;
  });
  $("tabla-codigos").querySelector("tbody").innerHTML = filas.join("");
}

function dibujar() {
  if (!datos) return;
  detenerConstruccion();
  const lienzo = $("lienzo-arbol"), cons = $("construccion");
  const enConstruccion = vista === "construccion";
  lienzo.classList.toggle("oculto", enConstruccion);
  cons.classList.toggle("oculto", !enConstruccion);
  $("controles-zoom").style.visibility = enConstruccion || vista === "explorador" ? "hidden" : "visible";
  if (enConstruccion) {
    vistaActual = { resaltar() {} };
    montarConstruccion(cons, datos);
    $("info-arbol").textContent = `${datos.fusiones.length} uniones voraces`;
    return;
  }
  if (vista === "radial") vistaActual = dibujarRadial(lienzo, datos.arbol, escala);
  else if (vista === "explorador") vistaActual = dibujarExplorador(lienzo, datos.arbol);
  else vistaActual = dibujarJerarquico(lienzo, datos.arbol, escala);
  $("info-arbol").textContent = vistaActual.texto + (vista !== "explorador" ? ` · zoom ${Math.round(escala * 100)} %` : "");
  if (seleccion) vistaActual.resaltar(seleccion);
}

function cambiarZoom(f) {
  if (!datos) return;
  escala = Math.min(3, Math.max(0.2, escala * f));
  dibujar();
}

function actualizarMetricas() {
  $("m-original").textContent = formatoBytes(datos.original);
  $("m-original-sub").textContent = `${miles(datos.original * 8)} bits (${datos.fijo.toFixed(0)} b/car)`;
  $("m-huf").textContent = comp ? formatoBytes(comp.huf) : "—";
  $("m-huf-sub").textContent = comp ? `${miles(comp.bits)} bits + tabla` : "presiona CODIFICAR";
  $("m-ahorro").textContent = comp ? comp.ahorro.toFixed(2) + " %" : "—";
  $("m-ahorro-sub").textContent = comp ? `${formatoBytes(datos.original - comp.huf)} ahorrados` : "—";
  $("m-entropia").textContent = datos.entropia.toFixed(3) + " b";
  $("m-bits").textContent = `Prom. código: ${datos.prom.toFixed(3)} bits · ef. ${datos.eficiencia.toFixed(1)} %`;
  const idioma = datos.idioma;
  $("m-idioma").textContent = idioma.codigo ? idioma.nombre : "No identificado";
  $("m-idioma-sub").textContent = idioma.codigo
    ? `${idioma.confianza.toFixed(0)} % de confianza` + (idioma.declarado_gutenberg ? ` · Gutenberg: ${idioma.declarado_gutenberg}` : "")
    : "texto muy corto";
  const v = $("m-verif");
  if (dec && dec.identico !== null) {
    v.textContent = dec.identico ? "✔ Idénticos" : "✘ Difieren";
    v.className = "tm-valor " + (dec.identico ? "fucsia" : "rosa");
    $("m-verif-sub").textContent = `decodificado en ${(dec.t_dec * 1000).toFixed(0)} ms`;
  } else {
    v.textContent = "—";
    v.className = "tm-valor";
    $("m-verif-sub").textContent = "Se comprueba byte por byte";
  }
  const pct = comp ? Math.max(0, Math.min(100, comp.ahorro)) : 0;
  $("progreso-relleno").style.width = pct + "%";
  $("progreso-etiqueta").textContent = comp ? `${pct.toFixed(1)} % de reducción` : "0 %";

  const filas = [
    ["Tamaño original (.txt)", `${formatoBytes(datos.original)} (${miles(datos.original)} B)`],
    ["Bits codificados (solo datos)", comp ? `${formatoBytes(comp.datos)} (${miles(comp.bits)} bits)` : "—"],
    ["Archivo .mc (datos + tabla)", comp ? `${formatoBytes(comp.huf)} (${miles(comp.huf)} B)` : "—"],
    ["Razón de compresión", comp ? comp.razon.toFixed(3) + " : 1" : "—"],
    ["Espacio ahorrado", comp ? comp.ahorro.toFixed(2) + " %" : "—"],
    ["Bits promedio por carácter", datos.prom.toFixed(4) + " bits"],
    ["Bits por carácter sin comprimir", datos.fijo.toFixed(2) + " bits"],
    ["Entropía de Shannon", datos.entropia.toFixed(4) + " bits"],
    ["Eficiencia del código (H / L)", datos.eficiencia.toFixed(2) + " %"],
    ["Árbol: hojas · nodos · altura", `${datos.hojas} · ${datos.nodos.length} · ${datos.altura}`],
    ["Idioma detectado", datos.idioma.codigo ? `${datos.idioma.nombre} (${datos.idioma.confianza.toFixed(0)} %)` : "—"],
    ["Tiempo de análisis", (datos.t_analisis * 1000).toFixed(1) + " ms"],
    ["Tiempo de codificación", comp ? (comp.t_cod * 1000).toFixed(1) + " ms" : "—"],
    ["Tiempo de decodificación", dec ? (dec.t_dec * 1000).toFixed(1) + " ms" : "—"],
    ["Decodificado = original", dec && dec.identico !== null ? (dec.identico ? "✔ idénticos" : "✘ difieren") : "—"],
  ];
  $("tabla-resultados").querySelector("tbody").innerHTML =
    filas.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join("");
  graficar();
}

function graficar() {
  const barras = [["Original", datos.original, "#64748b"]];
  if (comp) {
    barras.push(["Comprimido .mc", comp.huf, "url(#g-barra)"]);
    barras.push(["Solo datos", comp.datos, "#a855f7"]);
  }
  const W = 520, H = 320, base = 268, techo = 64, max = Math.max(...barras.map((b) => b[1]));
  const ancho = 110, sep = 160;
  let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="Fira Code, monospace">
    <defs><linearGradient id="g-barra" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#e11d48"/><stop offset="1" stop-color="#d946ef"/></linearGradient></defs>
    <text x="10" y="22" font-size="13" font-weight="600" fill="#e879f9" letter-spacing="1">COMPARACIÓN DE TAMAÑOS</text>`;
  barras.forEach(([nombre, valor, color], i) => {
    const h = (base - techo) * valor / max, x = 30 + i * sep;
    svg += `<rect x="${x}" y="${base - h}" width="${ancho}" height="${h}" rx="6" fill="${color}" style="filter:drop-shadow(0 0 8px rgba(217,70,239,.35))"/>`;
    svg += `<text x="${x + ancho / 2}" y="${base - h - 9}" text-anchor="middle" font-size="13" font-weight="700" fill="#f3e8ee">${formatoBytes(valor)}</text>`;
    svg += `<text x="${x + ancho / 2}" y="${base + 20}" text-anchor="middle" font-size="11" fill="rgba(249,168,212,.65)">${nombre}</text>`;
  });
  svg += `<line x1="20" x2="${W - 10}" y1="${base}" y2="${base}" stroke="rgba(217,70,239,.3)"/></svg>`;
  $("grafica-tamanos").innerHTML = svg;
}

function recorte(muestra, total) {
  return muestra + (total > muestra.length ? `\n\n[… vista recortada, ${miles(total)} caracteres en total]` : "");
}
