// Pestaña "Ahorro interactivo": muestra de varias formas cuánto espacio se
// ahorra al comprimir con Huffman.

import { escaparHTML, miles, formatoBytes } from "./python.js";

let datos = null, comp = null, raiz = null, modoContrib = "ahorran";
const VENTANA = 48;
const codificador = new TextEncoder();
const bitsOriginal = (c) => codificador.encode(c).length * 8;
const binario = (c) => [...codificador.encode(c)].map((b) => b.toString(2).padStart(8, "0")).join(" ");

export function montarAhorro(contenedor, analisis, compresion) {
  datos = analisis;
  comp = compresion;
  raiz = contenedor;
  const n = datos.curva.length - 1;
  contenedor.innerHTML = `
    <div class="ahorro">
      <div class="tarjeta-oscura">
        <h3><svg class="ico"><use href="#i-comprimir"/></svg> Ahorro total</h3>
        <div class="gran-ahorro"><strong class="degradado" data-a="porcentaje"></strong><span data-a="frase"></span></div>
        <div class="barras-comparacion" data-a="barras-total"></div>
        <p class="pequeno tenue" data-a="nota"></p>
      </div>

      <div class="tarjeta-oscura">
        <h3><svg class="ico"><use href="#i-libro"/></svg> Calculadora</h3>
        <div class="calculadora">Si comprimes <input type="number" min="1" value="1000" data-a="libros"> libros como este, ahorras <strong class="degradado" data-a="calc"></strong></div>
        <p class="pequeno tenue" data-a="calc-extra"></p>
        <div class="barras-comparacion" data-a="calc-barras"></div>
      </div>

      <div class="tarjeta-oscura ahorro__ancho">
        <h3><svg class="ico"><use href="#i-grafica"/></svg> Recorre el texto</h3>
        <p>Mueve el control (o pasa el mouse sobre la gráfica) para ver cuántos bits ocupa el texto hasta ese punto,
          sin comprimir y con Huffman. El área rosa es el espacio que te ahorras.</p>
        <div class="deslizador"><span>Inicio</span><input type="range" min="0" max="${n}" value="${n}" data-a="rango"><span>Final</span></div>
        <div class="barras-comparacion" data-a="barras-parcial"></div>
        <div class="curva" data-a="curva"></div>
      </div>

      <div class="tarjeta-oscura ahorro__ancho">
        <h3><svg class="ico"><use href="#i-bits"/></svg> Carácter por carácter</h3>
        <p>Cada carácter muestra sus bits sin comprimir (gris, 8 por byte en UTF-8) y sus bits con Huffman (morado;
          rojo si el código es más largo que el original). Pasa el mouse sobre un carácter para ver su código.</p>
        <div class="deslizador"><span>Posición</span><input type="range" min="0" max="${Math.max(0, datos.muestra.length - VENTANA)}" value="0" data-a="pos"><span data-a="pos-txt"></span></div>
        <div class="ventana" data-a="ventana"></div>
        <div class="detalle-car" data-a="detalle">&nbsp;</div>
        <div class="ventana-resumen" data-a="ventana-resumen"></div>
      </div>

      <div class="tarjeta-oscura ahorro__ancho">
        <div class="titulo-seccion" style="margin:0">
          <h3><svg class="ico"><use href="#i-tabla"/></svg> ¿Qué caracteres ahorran más espacio?</h3>
          <div class="segmentado" data-a="modo">
            <button class="activo" data-m="ahorran">Ahorran más</button>
            <button data-m="cuestan">Cuestan más</button>
          </div>
        </div>
        <p>Ahorro de cada carácter = frecuencia × (bits originales − bits de su código Huffman).</p>
        <div class="contrib" data-a="contrib"></div>
      </div>
    </div>`;

  const a = (k) => contenedor.querySelector(`[data-a="${k}"]`);
  a("rango").oninput = pintarParcial;
  a("pos").oninput = pintarVentana;
  a("libros").oninput = pintarCalculadora;
  a("modo").onclick = (e) => {
    const b = e.target.closest("button[data-m]");
    if (!b) return;
    modoContrib = b.dataset.m;
    a("modo").querySelectorAll("button").forEach((x) => x.classList.toggle("activo", x === b));
    pintarContrib();
  };
  a("ventana").addEventListener("mouseover", (e) => {
    const celda = e.target.closest(".vc");
    if (celda) mostrarDetalle(celda.dataset.car);
  });

  pintarTotal();
  pintarCalculadora();
  pintarParcial();
  pintarVentana();
  pintarContrib();
}

function q(k) { return raiz.querySelector(`[data-a="${k}"]`); }

function barras(filas) {
  const max = Math.max(...filas.map((f) => f[1]), 1);
  return filas.map(([nombre, valor, clase, texto]) =>
    `<div class="bc-fila"><span>${nombre}</span><div class="bc-barra bc-barra--${clase}"><i style="width:${(valor / max) * 100}%"></i></div>` +
    `<span class="bc-valor">${texto}</span></div>`).join("");
}

function pintarTotal() {
  const [, ori, huf] = datos.curva[datos.curva.length - 1];
  const original = datos.original;
  const comprimido = comp ? comp.huf : Math.ceil(huf / 8);
  const ahorro = (1 - comprimido / original) * 100;
  q("porcentaje").textContent = ahorro.toFixed(2) + " %";
  q("frase").textContent = `${formatoBytes(original)} → ${formatoBytes(comprimido)} · te ahorras ${formatoBytes(original - comprimido)}`;
  q("barras-total").innerHTML = barras([
    ["Original", original, "original", formatoBytes(original)],
    ["Huffman", comprimido, "huffman", formatoBytes(comprimido)],
  ]);
  q("nota").textContent = comp
    ? `Medido con el archivo .mc real (incluye la tabla de frecuencias). Por cada 8 bits originales se usan ${(datos.prom).toFixed(2)}.`
    : "Estimado con los códigos. Presiona CODIFICAR para medir el archivo .mc real.";
}

function pintarCalculadora() {
  const libros = Math.max(1, Number(q("libros").value) || 1);
  const original = datos.original;
  const comprimido = comp ? comp.huf : Math.ceil(datos.curva[datos.curva.length - 1][2] / 8);
  q("calc").textContent = formatoBytes((original - comprimido) * libros);
  const caben = Math.floor(original / comprimido * 100) / 100;
  q("calc-extra").textContent = `En el espacio de ${miles(libros)} libros sin comprimir caben ${miles(Math.floor(libros * caben))} libros comprimidos (${caben.toFixed(2)}×).`;
  q("calc-barras").innerHTML = barras([
    ["Sin comprimir", original * libros, "original", formatoBytes(original * libros)],
    ["Con Huffman", comprimido * libros, "huffman", formatoBytes(comprimido * libros)],
  ]);
}

function pintarParcial() {
  const i = Number(q("rango").value);
  const [k, ori, huf] = datos.curva[i];
  const ahorro = ori ? (1 - huf / ori) * 100 : 0;
  q("barras-parcial").innerHTML =
    `<p class="pequeno mono" style="margin-bottom:4px">Primeros <b>${miles(k)}</b> de ${miles(datos.caracteres)} caracteres · ahorro <b class="fucsia">${ahorro.toFixed(2)} %</b></p>` +
    barras([
      ["Original", ori, "original", `${miles(ori)} bits`],
      ["Huffman", huf, "huffman", `${miles(huf)} bits`],
    ]);
  pintarCurva(i);
}

function pintarCurva(i) {
  const W = 900, H = 230, izq = 64, der = 16, arr = 16, aba = 32;
  const puntos = datos.curva;
  const maxX = puntos[puntos.length - 1][0], maxY = puntos[puntos.length - 1][1];
  const X = (v) => izq + (v / maxX) * (W - izq - der);
  const Y = (v) => H - aba - (v / maxY) * (H - arr - aba);
  const linea = (j) => puntos.map((p, n) => `${n ? "L" : "M"}${X(p[0]).toFixed(1)},${Y(p[j]).toFixed(1)}`).join("");
  const area = linea(1) + puntos.slice().reverse().map((p) => `L${X(p[0]).toFixed(1)},${Y(p[2]).toFixed(1)}`).join("") + "Z";
  const [k, ori, huf] = puntos[i];
  const ejeY = [0, 0.5, 1].map((f) => {
    const v = maxY * f;
    return `<line x1="${izq}" x2="${W - der}" y1="${Y(v)}" y2="${Y(v)}" stroke="rgba(168,85,247,.12)"/>` +
      `<text x="${izq - 8}" y="${Y(v) + 4}" text-anchor="end" font-size="10" fill="rgba(249,168,212,.5)">${formatoBytes(v / 8)}</text>`;
  }).join("");
  q("curva").innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="Fira Code, monospace">
      <defs><linearGradient id="g-huf" x1="0" x2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset=".5" stop-color="#d946ef"/><stop offset="1" stop-color="#a855f7"/></linearGradient></defs>
      ${ejeY}
      <path d="${area}" fill="rgba(244,63,94,.16)"/>
      <path d="${linea(1)}" fill="none" stroke="#94a3b8" stroke-width="2"/>
      <path d="${linea(2)}" fill="none" stroke="url(#g-huf)" stroke-width="2.5"/>
      <line x1="${X(k)}" x2="${X(k)}" y1="${arr}" y2="${H - aba}" stroke="#fde047" stroke-dasharray="4 4"/>
      <circle cx="${X(k)}" cy="${Y(ori)}" r="5" fill="#94a3b8"/>
      <circle cx="${X(k)}" cy="${Y(huf)}" r="5" fill="#e879f9" stroke="#fff" stroke-width="1.5"/>
      <text x="${izq}" y="${H - 8}" font-size="10" fill="rgba(249,168,212,.5)">0</text>
      <text x="${W - der}" y="${H - 8}" font-size="10" fill="rgba(249,168,212,.5)" text-anchor="end">${miles(maxX)} caracteres</text>
      <text x="${W - der - 4}" y="${Y(maxY) + 14}" font-size="11" fill="#cbd5e1" text-anchor="end">sin comprimir</text>
      <text x="${W - der - 4}" y="${Y(puntos[puntos.length - 1][2]) + 16}" font-size="11" fill="#f0abfc" text-anchor="end">Huffman</text>
      <rect x="${izq}" y="${arr}" width="${W - izq - der}" height="${H - arr - aba}" fill="transparent" data-a="zona"/>
    </svg>`;
  const svg = q("curva").querySelector("svg");
  const mover = (e) => {
    const r = svg.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * W;
    const v = Math.max(0, Math.min(1, (x - izq) / (W - izq - der))) * maxX;
    let mejor = 0;
    puntos.forEach((p, n) => { if (Math.abs(p[0] - v) < Math.abs(puntos[mejor][0] - v)) mejor = n; });
    if (mejor !== Number(q("rango").value)) {
      q("rango").value = mejor;
      pintarParcial();
    }
  };
  svg.addEventListener("mousemove", mover);
}

function pintarVentana() {
  const inicio = Number(q("pos").value);
  const trozo = [...datos.muestra.slice(inicio, inicio + VENTANA)];
  let ori = 0, huf = 0;
  q("ventana").innerHTML = trozo.map((c) => {
    const codigo = datos.codigos_crudos[c] || "";
    const bo = bitsOriginal(c), bh = codigo.length;
    ori += bo; huf += bh;
    const visible = c === " " ? "␣" : c === "\n" ? "↵" : c === "\r" ? "␍" : c === "\t" ? "⇥" : c;
    return `<div class="vc" data-car="${escaparHTML(c)}" title="${escaparHTML(visible)} → ${codigo}">
      <span class="vc-car">${escaparHTML(visible)}</span>
      <span class="vc-bits vc-bits--ori">${"<i></i>".repeat(bo)}</span>
      <span class="vc-bits vc-bits--huf">${Array.from({ length: bh }, (_, k) => `<i class="${k >= bo ? "mas" : ""}"></i>`).join("")}</span>
    </div>`;
  }).join("");
  q("pos-txt").textContent = `caracteres ${miles(inicio + 1)}–${miles(inicio + trozo.length)}`;
  q("ventana-resumen").innerHTML = `En esta ventana: <b>${miles(ori)}</b> bits sin comprimir → <b class="fucsia">${miles(huf)}</b> bits con Huffman · ahorro <b class="rosa">${ori ? ((1 - huf / ori) * 100).toFixed(1) : 0} %</b>`;
}

function mostrarDetalle(c) {
  const codigo = datos.codigos_crudos[c] || "";
  const bo = bitsOriginal(c);
  const visible = c === " " ? "espacio" : c === "\n" ? "salto de línea" : c === "\r" ? "retorno" : `'${c}'`;
  const diferencia = bo - codigo.length;
  q("detalle").innerHTML = `<b>${escaparHTML(visible)}</b> · original ${bo} bits (<span class="tenue">${binario(c)}</span>) → Huffman <b class="fucsia">${codigo.length} bits</b> (<span class="codigo">${codigo}</span>) · ` +
    (diferencia >= 0 ? `ahorra <b class="fucsia">${diferencia}</b> bits cada vez que aparece` : `cuesta <b class="rosa">${-diferencia}</b> bits más, pero aparece muy poco`);
}

function pintarContrib() {
  const lista = datos.tabla.map((f) => {
    const crudo = Object.keys(datos.codigos_crudos).find((k) => datos.codigos_crudos[k] === f.codigo) ?? f.car;
    const bo = bitsOriginal(crudo);
    return { car: f.car, frec: f.frec, codigo: f.codigo, ahorro: f.frec * (bo - f.codigo.length) };
  });
  const elegidos = modoContrib === "ahorran"
    ? lista.filter((x) => x.ahorro > 0).sort((a, b) => b.ahorro - a.ahorro).slice(0, 12)
    : lista.filter((x) => x.ahorro < 0).sort((a, b) => a.ahorro - b.ahorro).slice(0, 12);
  if (!elegidos.length) {
    q("contrib").innerHTML = `<p class="tenue pequeno">Ningún carácter ${modoContrib === "ahorran" ? "ahorra" : "cuesta más"} espacio.</p>`;
    return;
  }
  const max = Math.max(...elegidos.map((x) => Math.abs(x.ahorro)));
  q("contrib").innerHTML = elegidos.map((x) =>
    `<div class="contrib-fila"><span><b>${escaparHTML(x.car.length > 10 ? x.car.slice(0, 10) : x.car)}</b></span>` +
    `<div><div class="barra-c ${x.ahorro < 0 ? "barra-c--neg" : ""}" style="width:${(Math.abs(x.ahorro) / max) * 100}%"></div></div>` +
    `<span class="bc-valor">${x.ahorro > 0 ? "−" : "+"}${formatoBytes(Math.abs(x.ahorro) / 8)}</span></div>`).join("") +
    (modoContrib === "cuestan"
      ? `<p class="tenue pequeno" style="margin-top:6px">Estos caracteres son tan raros que su código es más largo que 8 bits, pero como casi no aparecen el costo es mínimo comparado con lo que ahorran los frecuentes.</p>`
      : "");
}

/** Se llama cuando se codifica (para usar el tamaño real del .mc). */
export function actualizarAhorro(compresion) {
  if (!datos || !raiz) return;
  comp = compresion;
  pintarTotal();
  pintarCalculadora();
}
