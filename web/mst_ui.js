// Pestaña de árbol de expansión mínima: Kruskal y Prim (calculados en Python),
// dibujados paso a paso en SVG.

import { py, ocupado, listo } from "./python.js";

const $ = (id) => document.getElementById(id);
const ANCHO = 700, ALTO = 480;
let g = null;          // resultado de puente.grafo()
let paso = 0;
let animacion = null;

const algoritmo = () => document.querySelector('input[name="algoritmo"]:checked').value;

export function iniciarMST() {
  $("mst-generar").addEventListener("click", () => calcular(true));
  $("mst-reiniciar").addEventListener("click", () => calcular(false));
  $("mst-completo").addEventListener("click", () => { detener(); while (siguiente()); });
  $("mst-paso").addEventListener("click", () => { detener(); siguiente(); });
  $("mst-animar").addEventListener("click", alternarAnimacion);
  document.querySelectorAll('input[name="algoritmo"]').forEach((r) => r.addEventListener("change", () => calcular(false)));
  $("mst-inicio").addEventListener("change", () => calcular(false));
  listo.then(() => calcular(true)).catch(() => {});
}

async function calcular(nuevo) {
  detener();
  const n = Math.max(3, Math.min(40, parseInt($("mst-nodos").value, 10) || 12));
  $("mst-nodos").value = n;
  const semilla = $("mst-semilla").value === "" ? "None" : parseInt($("mst-semilla").value, 10);
  const inicio = nuevo ? 0 : Math.min(n - 1, parseInt($("mst-inicio").value || "0", 10));
  await ocupado("Calculando…", () => {
    g = py(`grafo(${n}, ${parseFloat($("mst-densidad").value)}, ${semilla}, "${algoritmo()}", ${inicio})`);
  });
  if (nuevo || $("mst-inicio").options.length !== n) {
    $("mst-inicio").innerHTML = g.etiquetas.map((e, i) => `<option value="${i}">${e}</option>`).join("");
    $("mst-inicio").value = String(inicio);
  }
  paso = 0;
  $("mst-tabla").querySelector("tbody").innerHTML = "";
  $("mst-peso").textContent = "—";
  $("mst-detalle").textContent = `${g.etiquetas.length} nodos · ${g.aristas.length} aristas`;
  dibujar();
}

function siguiente() {
  if (!g || paso >= g.pasos.length) { detener(); return false; }
  const [u, v, peso, ok] = g.pasos[paso++];
  const decision = ok ? "✔ se agrega" : algoritmo() === "Kruskal" ? "✘ formaría ciclo" : "✘ ya visitado";
  const fila = document.createElement("tr");
  fila.className = ok ? "si" : "no";
  fila.innerHTML = `<td class="num">${paso}</td><td>${g.etiquetas[u]}–${g.etiquetas[v]}</td><td class="num">${peso}</td><td>${decision}</td>`;
  $("mst-tabla").querySelector("tbody").appendChild(fila);
  const caja = fila.closest(".tabla-scroll");
  caja.scrollTop = caja.scrollHeight;
  const acumulado = g.pasos.slice(0, paso).filter((p) => p[3]).reduce((s, p) => s + p[2], 0);
  $("mst-peso").textContent = acumulado;
  if (paso === g.pasos.length) {
    const rechazadas = g.pasos.filter((p) => !p[3]).length;
    const otro = algoritmo() === "Kruskal" ? "Prim" : "Kruskal";
    $("mst-detalle").textContent =
      `${g.aristas_arbol} aristas en el árbol (n − 1)\n${g.pasos.length} evaluadas · ${rechazadas} rechazadas\n` +
      `Tiempo en Python: ${(g.tiempo * 1000).toFixed(2)} ms\n${otro}: peso ${g.otro_total} → ` +
      (g.otro_total === g.total ? "coinciden ✔" : "¡difieren!");
  }
  dibujar();
  return true;
}

function alternarAnimacion() {
  if (animacion) return detener();
  if (g && paso >= g.pasos.length) { calcular(false).then(alternarAnimacion); return; }
  $("mst-animar").innerHTML = '<svg class="ico"><use href="#i-pausa"/></svg><span>Pausa</span>';
  animacion = setInterval(() => { if (!siguiente()) detener(); }, 550);
}

function detener() {
  clearInterval(animacion);
  animacion = null;
  $("mst-animar").innerHTML = '<svg class="ico"><use href="#i-play"/></svg><span>Animar</span>';
}

function dibujar() {
  if (!g) return;
  const clave = (u, v) => (u < v ? u + "-" + v : v + "-" + u);
  const hechos = g.pasos.slice(0, paso);
  const aceptadas = new Set(hechos.filter((p) => p[3]).map((p) => clave(p[0], p[1])));
  const rechazadas = new Set(hechos.filter((p) => !p[3]).map((p) => clave(p[0], p[1])));
  const actual = paso && paso < g.pasos.length ? clave(hechos[paso - 1][0], hechos[paso - 1][1]) : null;
  const visitados = new Set();
  if (algoritmo() === "Prim" && paso) visitados.add(parseInt($("mst-inicio").value, 10));
  hechos.filter((p) => p[3]).forEach((p) => { visitados.add(p[0]); visitados.add(p[1]); });

  const P = g.posiciones;
  const ordenadas = [...g.aristas].sort((a, b) => aceptadas.has(clave(a[0], a[1])) - aceptadas.has(clave(b[0], b[1])));
  let svg = `<svg viewBox="0 0 ${ANCHO} ${ALTO}" xmlns="http://www.w3.org/2000/svg" font-family="Fira Code, monospace">`;
  for (const [u, v, peso] of ordenadas) {
    const k = clave(u, v);
    let color = "rgba(244,114,182,.22)", grosor = 1.5, guiones = "", texto = "rgba(249,168,212,.55)", brillo = "";
    if (k === actual) { color = "#fde047"; grosor = 5; texto = color; brillo = 'style="filter:drop-shadow(0 0 6px #fde047)"'; }
    else if (aceptadas.has(k)) { color = "#e879f9"; grosor = 4; texto = color; brillo = 'style="filter:drop-shadow(0 0 5px rgba(232,121,249,.8))"'; }
    else if (rechazadas.has(k)) { color = "#f43f5e"; grosor = 1.6; guiones = 'stroke-dasharray="4 3"'; texto = color; }
    const [x1, y1] = P[u], [x2, y2] = P[v];
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${grosor}" ${guiones} ${brillo} stroke-linecap="round"/>`;
    svg += `<rect x="${mx - 11}" y="${my - 8}" width="22" height="16" rx="4" fill="#0b0310" stroke="rgba(112,26,117,.6)"/>`;
    svg += `<text x="${mx}" y="${my + 4}" text-anchor="middle" font-size="11" fill="${texto}" font-weight="${aceptadas.has(k) ? 700 : 400}">${peso}</text>`;
  }
  P.forEach(([x, y], i) => {
    const visto = visitados.has(i);
    svg += `<circle cx="${x}" cy="${y}" r="15" fill="${visto ? "#4a044e" : "#0f0210"}" stroke="${visto ? "#e879f9" : "#a855f7"}" stroke-width="${visto ? 2.4 : 1.6}" style="filter:drop-shadow(0 0 ${visto ? 9 : 4}px ${visto ? "rgba(232,121,249,.8)" : "rgba(126,34,206,.8)"})"/>`;
    svg += `<text x="${x}" y="${y + 4}" text-anchor="middle" font-size="11" font-weight="700" fill="${visto ? "#fff" : "#f3e8ee"}">${g.etiquetas[i]}</text>`;
  });
  $("lienzo-grafo").innerHTML = svg + "</svg>";
}
