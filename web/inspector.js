// Inspector de archivos .mc: muestra la estructura interna del archivo comprimido
// SIN el .txt original. La descompresión solo ocurre al presionar DESCOMPRIMIR.

import { CARPETA, py, escribir, leer, borrar, ocupado, formatoBytes, miles, descargar, escaparHTML, aviso } from "./python.js";
import { dibujarJerarquico, arrastrable } from "./arbol.js";
import { marcarHasta, irAPanel } from "./flujo.js";

const $ = (id) => document.getElementById(id);
const RUTA_INSP = CARPETA + "/inspeccion.mc";
const RUTA_REC = CARPETA + "/inspeccion_recuperado.txt";
const RUTA_COMPRIMIDO = CARPETA + "/comprimido.mc";

const COLORES = {
  "Firma y versión": "#f43f5e",
  "Tamaños, bits y relleno": "#fb923c",
  "Fecha": "#fde047",
  "SHA-256 del original": "#4ade80",
  "Codificación y nombre": "#22d3ee",
  "Codificación": "#22d3ee",
  "Tabla de frecuencias": "#c084fc",
  "Relleno": "#fb923c",
  "Datos comprimidos": "#e879f9",
};

let info = null, nombreArchivo = "", nombreActual = "", escala = 1, recuperado = false;

export function iniciarInspector() {
  const zona = $("zona-mc");
  zona.addEventListener("dragover", (e) => { e.preventDefault(); zona.classList.add("encima"); });
  zona.addEventListener("dragleave", () => zona.classList.remove("encima"));
  zona.addEventListener("drop", (e) => {
    e.preventDefault();
    zona.classList.remove("encima");
    if (e.dataTransfer.files.length) abrirArchivo(e.dataTransfer.files[0]);
  });
  $("archivo-mc").addEventListener("change", (e) => {
    if (e.target.files.length) abrirArchivo(e.target.files[0]);
    e.target.value = "";
  });
  $("insp-usar-actual").addEventListener("click", () => abrirEnInspector(leer(RUTA_COMPRIMIDO), nombreActual));
  $("insp-descomprimir").addEventListener("click", descomprimir);
  $("insp-bajar").addEventListener("click", () =>
    descargar(leer(RUTA_REC), (info?.nombre_original || nombreArchivo.replace(/\.mc$/i, ".txt")).replace(/\.txt$/i, "") + "_recuperado.txt", "text/plain"));
  $("insp-zoom-mas").addEventListener("click", () => { escala = Math.min(3, escala * 1.25); dibujarArbol(); });
  $("insp-zoom-menos").addEventListener("click", () => { escala = Math.max(0.2, escala * 0.8); dibujarArbol(); });
  arrastrable($("insp-lienzo"));
  $("insp-pestanas").addEventListener("click", (e) => {
    const b = e.target.closest("[data-isub]");
    if (b) mostrarSub(b.dataset.isub);
  });
  // La sección de Huffman avisa cuando generó un .mc
  document.addEventListener("mc-generado", (e) => {
    nombreActual = e.detail.nombre;
    $("insp-usar-actual").disabled = false;
  });
}

async function abrirArchivo(archivo) {
  if (!archivo.name.toLowerCase().endsWith(".mc")) {
    aviso("El Inspector solo abre archivos .mc", "error");
    return;
  }
  await abrirEnInspector(new Uint8Array(await archivo.arrayBuffer()), archivo.name);
}

/** Carga un .mc (bytes) en el Inspector y muestra su estructura. */
export async function abrirEnInspector(bytes, nombre) {
  irAPanel("panel-inspector");
  try {
    await ocupado("Leyendo el encabezado y la tabla de frecuencias…", () => {
      borrar(RUTA_REC);
      escribir(RUTA_INSP, bytes);
      info = py("inspeccionar()");
    });
  } catch (error) {
    console.error(error);
    aviso("No es un archivo .mc válido de El Huffmanificador.", "error");
    return;
  }
  nombreArchivo = nombre;
  recuperado = false;
  escala = 1;
  pintar();
  marcarHasta(5);
  aviso(`Archivo inspeccionado: ${info.simbolos} símbolos, ${miles(info.bits_validos)} bits codificados.`, "ok");
}

function mostrarSub(id) {
  document.querySelectorAll("#insp-pestanas .pestana").forEach((b) => b.classList.toggle("activa", b.dataset.isub === id));
  document.querySelectorAll(".isubpanel").forEach((p) => p.classList.toggle("activo", p.id === id));
  if (id === "isub-arbol") dibujarArbol();
}

function estado(texto) {
  $("insp-estado").innerHTML = `<i class="punto"></i>${texto}`;
}

function pintar() {
  $("insp-vacio").classList.add("oculto");
  const ext = (nombreArchivo.match(/\.[^.]+$/) || [""])[0];
  $("insp-nombre").textContent = nombreArchivo;
  $("insp-detalle").textContent = `Extensión ${ext} · formato HMC versión ${info.version}` +
    (info.nombre_original ? ` · original: ${info.nombre_original}` : "") + (info.fecha ? ` · creado ${info.fecha}` : "");
  const o = info.tamano_original;
  $("i-original").textContent = o === null ? "no guardado" : formatoBytes(o);
  $("i-original-sub").textContent = o === null ? "formato v1" : `${miles(o)} bytes`;
  $("i-mc").textContent = formatoBytes(info.tamano_comprimido);
  $("i-mc-sub").textContent = `${miles(info.tamano_comprimido)} bytes`;
  $("i-ahorro").textContent = info.ahorro === null ? "—" : info.ahorro.toFixed(2) + " %";
  $("i-ahorro-sub").textContent = info.ahorrados === null ? "—" : `${miles(info.ahorrados)} B (${formatoBytes(info.ahorrados)})`;
  $("i-simbolos").textContent = miles(info.simbolos);
  $("i-simbolos-sub").textContent = `${miles(info.caracteres)} caracteres`;
  $("insp-descomprimir").disabled = false;
  $("insp-bajar").disabled = true;
  estado("ESTRUCTURA LEÍDA");
  $("insp-verificacion").innerHTML = "";
  $("insp-texto").innerHTML = '<span class="tenue cursiva">Presiona DESCOMPRIMIR para recuperar el texto.</span>';

  pintarEstructura();
  pintarBytes();
  $("insp-tabla").querySelector("tbody").innerHTML = info.tabla.map((f) =>
    `<tr><td><b>${escaparHTML(f.car)}</b></td><td class="num fucsia">${miles(f.frec)}</td>` +
    `<td>${(f.prob * 100).toFixed(2)} %<span class="mini-barra"><i style="width:${Math.min(100, f.prob * 400)}%"></i></span></td>` +
    `<td class="codigo">${f.codigo}</td><td class="num tenue">${f.codigo.length}</td></tr>`).join("");
  mostrarSub("isub-estructura");
}

function pintarEstructura() {
  const filas = [
    ["Nombre y extensión", escaparHTML(nombreArchivo)],
    ["Formato / versión", `HMC · versión ${info.version}`],
    ["Archivo original", escaparHTML(info.nombre_original || "—")],
    ["Codificación del texto", escaparHTML(info.codificacion)],
    ["Fecha de creación", info.fecha || "—"],
    ["Tamaño original", info.tamano_original === null ? "no guardado (v1)" : `${miles(info.tamano_original)} B (${formatoBytes(info.tamano_original)})`],
    ["Tamaño comprimido", `${miles(info.tamano_comprimido)} B (${formatoBytes(info.tamano_comprimido)})`],
    ["Bytes ahorrados", info.ahorrados === null ? "—" : `${miles(info.ahorrados)} B (${formatoBytes(info.ahorrados)})`],
    ["Porcentaje de compresión", info.ahorro === null ? "—" : `${info.ahorro.toFixed(2)} % de reducción`],
    ["Razón de compresión", info.razon === null ? "—" : `${info.razon.toFixed(3)} : 1`],
    ["Caracteres del texto", miles(info.caracteres)],
    ["Símbolos distintos", miles(info.simbolos)],
    ["Bits codificados válidos", miles(info.bits_validos)],
    ["Bits de relleno (último byte)", info.relleno],
    ["Bytes de datos comprimidos", `${miles(info.bytes_datos)} B = ⌈${miles(info.bits_validos)} / 8⌉`],
    ["Bits promedio por símbolo", `${info.prom.toFixed(4)} (entropía ${info.entropia.toFixed(4)})`],
    ["SHA-256 del original", info.sha256 ? `<span class="hash">${info.sha256}</span>` : "no guardado"],
  ];
  const total = info.tamano_comprimido;
  const minimo = 6;  // % de ancho mínimo para que se vean las secciones pequeñas
  const anchos = info.secciones.map(([, , largo]) => Math.max(minimo, (largo / total) * 100));
  const suma = anchos.reduce((a, b) => a + b, 0);
  const barra = info.secciones.map(([nombre, , largo], i) =>
    `<div class="mapa__seg" style="width:${(anchos[i] / suma) * 100}%;background:${COLORES[nombre] || "#94a3b8"}" title="${nombre}: ${miles(largo)} B"></div>`).join("");
  const leyenda = info.secciones.map(([nombre, offset, largo]) =>
    `<tr><td><i class="punto-color" style="background:${COLORES[nombre] || "#94a3b8"}"></i>${nombre}</td>` +
    `<td class="num">${miles(offset)}</td><td class="num">${miles(largo)} B</td><td class="num">${((largo / total) * 100).toFixed(2)} %</td></tr>`).join("");

  $("insp-estructura").innerHTML = `
    <div class="dos-columnas dos-columnas--resultados">
      <div class="tarjeta-oscura">
        <h3><svg class="ico"><use href="#i-tabla"/></svg> Metadatos leídos del encabezado</h3>
        <table class="tabla tabla--datos"><tbody>${filas.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join("")}</tbody></table>
      </div>
      <div class="tarjeta-oscura">
        <h3><svg class="ico"><use href="#i-capas"/></svg> Mapa del archivo</h3>
        <p>Cómo se reparten los ${miles(total)} bytes del .mc. Las secciones pequeñas se dibujan con un ancho mínimo para que se vean.</p>
        <div class="mapa">${barra}</div>
        <table class="tabla"><thead><tr><th>Sección</th><th class="num">Offset</th><th class="num">Tamaño</th><th class="num">% del archivo</th></tr></thead>
          <tbody>${leyenda}</tbody></table>
        <p class="pequeno tenue">El texto original no se guarda: solo la tabla de frecuencias (para reconstruir el árbol) y los bits codificados.</p>
      </div>
    </div>`;
}

function seccionDe(offset) {
  for (const [nombre, inicio, largo] of info.secciones) if (offset >= inicio && offset < inicio + largo) return nombre;
  return "";
}

function volcado(hex, base) {
  const bytes = hex.match(/../g) || [];
  let html = "";
  for (let i = 0; i < bytes.length; i += 16) {
    const fila = bytes.slice(i, i + 16);
    const celdas = fila.map((b, j) => {
      const color = COLORES[seccionDe(base + i + j)] || "#94a3b8";
      return `<span style="color:${color}">${b}</span>`;
    }).join(" ");
    const ascii = fila.map((b) => {
      const v = parseInt(b, 16);
      return v >= 32 && v < 127 ? escaparHTML(String.fromCharCode(v)) : "·";
    }).join("");
    html += `<div class="hex__fila"><span class="hex__off">${(base + i).toString(16).padStart(8, "0")}</span>` +
      `<span class="hex__bytes">${celdas}</span><span class="hex__ascii">${ascii}</span></div>`;
  }
  return html;
}

function pintarBytes() {
  const bits = info.muestra_bits;
  let grupos = "";
  for (let i = 0; i < bits.length; i += 8) {
    grupos += [...bits.slice(i, i + 8)].map((b) => `<span class="${b === "0" ? "c" : "u"}">${b}</span>`).join("") + " ";
  }
  $("insp-bytes").innerHTML = `
    <div class="tarjeta-oscura" style="margin-bottom:16px">
      <h3><svg class="ico"><use href="#i-bits"/></svg> Inicio del archivo (encabezado y tabla) en hexadecimal</h3>
      <p>Cada color es una sección del formato (ver «Mapa del archivo»). A la derecha, los mismos bytes como texto ASCII.</p>
      <div class="hex">${volcado(info.inicio_hex, 0)}</div>
    </div>
    <div class="tarjeta-oscura" style="margin-bottom:16px">
      <h3><svg class="ico"><use href="#i-bits"/></svg> Datos comprimidos (desde el byte ${miles(info.inicio_datos)})</h3>
      <div class="hex">${volcado(info.datos_hex, info.inicio_datos)}</div>
    </div>
    <div class="tarjeta-oscura">
      <h3><svg class="ico"><use href="#i-bits"/></svg> Primeros ${miles(bits.length)} de ${miles(info.bits_validos)} bits codificados</h3>
      <p>Para recuperar el texto se recorre el árbol con estos bits: 0 = izquierda, 1 = derecha. El último byte del archivo
        trae ${info.relleno} bit${info.relleno === 1 ? "" : "s"} de relleno que se ignoran.</p>
      <div class="caja-bits mono">${grupos}</div>
    </div>`;
}

function dibujarArbol() {
  if (!info) return;
  dibujarJerarquico($("insp-lienzo"), info.arbol, escala);
}

async function descomprimir() {
  let r;
  try {
    await ocupado("Descomprimiendo: recorriendo el árbol bit por bit…", () => { r = py("descomprimir_inspector()"); });
  } catch (error) {
    console.error(error);
    aviso("No se pudo descomprimir el archivo.", "error");
    return;
  }
  recuperado = true;
  const ok = (v) => v === null ? '<span class="tenue">no disponible</span>' : v ? '<b class="fucsia">✔ coincide</b>' : '<b class="rosa">✘ no coincide</b>';
  const integro = r.sha256_ok !== false && r.tamano_ok !== false;
  $("insp-verificacion").innerHTML = `
    <div class="tarjeta-oscura verificacion__caja ${integro ? "" : "verificacion__caja--mal"}">
      <h3>${integro ? "✔ Archivo íntegro: el texto recuperado es idéntico al original" : "✘ El archivo está dañado o fue modificado"}</h3>
      <table class="tabla tabla--datos"><tbody>
        <tr><td>Tamaño recuperado vs. tamaño original guardado</td><td>${miles(r.tamano)} B · ${ok(r.tamano_ok)}</td></tr>
        <tr><td>SHA-256 del texto recuperado</td><td><span class="hash">${r.sha256}</span></td></tr>
        <tr><td>SHA-256 guardado en el encabezado</td><td><span class="hash">${info.sha256 || "—"}</span> · ${ok(r.sha256_ok)}</td></tr>
        <tr><td>Caracteres recuperados · tiempo</td><td>${miles(r.caracteres)} · ${(r.t_dec * 1000).toFixed(0)} ms</td></tr>
      </tbody></table>
    </div>`;
  $("insp-texto").textContent = r.muestra + (r.caracteres > r.muestra.length ? `\n\n[… vista recortada, ${miles(r.caracteres)} caracteres en total]` : "");
  $("insp-bajar").disabled = false;
  estado(integro ? "VERIFICADO" : "DAÑADO");
  marcarHasta(6);
  mostrarSub("isub-texto");
  aviso(integro ? "Descompresión verificada con SHA-256: idéntico al original." : "La verificación falló: el archivo no coincide con su hash.", integro ? "ok" : "error");
}
