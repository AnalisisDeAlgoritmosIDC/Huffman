// Vista "Construcción paso a paso": muestra la cola de prioridad en cada paso
// del algoritmo voraz y resalta los dos nodos de menor frecuencia que se unen.

import { escaparHTML, miles } from "./python.js";
import { etiquetaCorta } from "./arbol.js";

let datos = null, paso = 0, temporizador = null, raizVista = null;

export function montarConstruccion(contenedor, analisis) {
  detener();
  datos = analisis;
  paso = 0;
  raizVista = contenedor;
  const total = datos.fusiones.length;
  contenedor.innerHTML = `
    <div class="cons-controles">
      <button class="btn-icono" data-c="inicio" title="Inicio"><svg class="ico"><use href="#i-ant"/></svg></button>
      <button class="btn btn--chico" data-c="atras">◀ Paso</button>
      <button class="btn btn--neon btn--chico" data-c="play"><svg class="ico"><use href="#i-play"/></svg><span>Reproducir</span></button>
      <button class="btn btn--chico" data-c="adelante">Paso ▶</button>
      <button class="btn-icono" data-c="fin" title="Final"><svg class="ico"><use href="#i-sig"/></svg></button>
      <input type="range" min="0" max="${total}" value="0" data-c="rango" aria-label="Paso">
      <span class="cons-estado" data-c="estado"></span>
    </div>
    <div class="cons-fusion" data-c="fusion"></div>
    <p class="tenue pequeno">Cola de prioridad (ordenada de menor a mayor frecuencia). Las fichas
      <span class="rosa">rosas</span> son caracteres; las <span class="violeta">moradas</span>, nodos internos ya unidos.</p>
    <div class="cons-cola" data-c="cola"></div>
    <div class="tabla-scroll" style="max-height:260px">
      <table class="tabla"><thead><tr><th class="num">Paso</th><th>Nodo menor</th><th>Segundo menor</th><th class="num">Nuevo nodo</th></tr></thead>
      <tbody data-c="tabla">${datos.pasos.map((p, i) =>
        `<tr data-i="${i}"><td class="num">${i + 1}</td><td>${escaparHTML(p[0])}</td><td>${escaparHTML(p[1])}</td><td class="num">${miles(p[2])}</td></tr>`).join("")}</tbody></table>
    </div>`;

  const c = (nombre) => contenedor.querySelector(`[data-c="${nombre}"]`);
  c("inicio").onclick = () => ir(0);
  c("fin").onclick = () => ir(total);
  c("atras").onclick = () => ir(paso - 1);
  c("adelante").onclick = () => ir(paso + 1);
  c("rango").oninput = (e) => ir(Number(e.target.value));
  c("play").onclick = alternar;
  contenedor.querySelector('[data-c="tabla"]').onclick = (e) => {
    const fila = e.target.closest("tr[data-i]");
    if (fila) ir(Number(fila.dataset.i));
  };
  pintar();
}

function ir(n) {
  paso = Math.max(0, Math.min(datos.fusiones.length, n));
  pintar();
}

function alternar() {
  if (temporizador) return detener();
  if (paso >= datos.fusiones.length) paso = 0;
  const boton = raizVista.querySelector('[data-c="play"]');
  boton.innerHTML = '<svg class="ico"><use href="#i-pausa"/></svg><span>Pausa</span>';
  const intervalo = Math.max(120, 9000 / datos.fusiones.length);
  temporizador = setInterval(() => {
    if (paso >= datos.fusiones.length) return detener();
    ir(paso + 1);
  }, intervalo);
}

export function detener() {
  clearInterval(temporizador);
  temporizador = null;
  const boton = raizVista?.querySelector('[data-c="play"]');
  if (boton) boton.innerHTML = '<svg class="ico"><use href="#i-play"/></svg><span>Reproducir</span>';
}

function nombre(id) {
  const n = datos.nodos[id];
  return n.c !== null ? `'${etiquetaCorta(n.c)}'` : `Σ${n.f}`;
}

function pintar() {
  const total = datos.fusiones.length;
  // Estado de la cola después de `paso` uniones
  const hojas = datos.nodos.length - total;
  const cola = new Set(Array.from({ length: hojas }, (_, i) => i));
  for (let k = 0; k < paso; k++) {
    const [a, b, nuevo] = datos.fusiones[k];
    cola.delete(a); cola.delete(b); cola.add(nuevo);
  }
  const siguiente = paso < total ? datos.fusiones[paso] : null;
  const recien = paso > 0 ? datos.fusiones[paso - 1][2] : -1;
  const ordenada = [...cola].sort((x, y) => datos.nodos[x].f - datos.nodos[y].f || x - y);

  const q = (n) => raizVista.querySelector(`[data-c="${n}"]`);
  q("rango").value = paso;
  q("estado").textContent = `Paso ${paso} de ${total} · ${cola.size} nodo${cola.size === 1 ? "" : "s"} en la cola`;
  q("fusion").innerHTML = siguiente
    ? `<span class="tenue">Siguiente unión voraz:</span>
       <span class="ficha ficha--elegida">${escaparHTML(nombre(siguiente[0]))} <b>${datos.nodos[siguiente[0]].f}</b></span> +
       <span class="ficha ficha--elegida">${escaparHTML(nombre(siguiente[1]))} <b>${datos.nodos[siguiente[1]].f}</b></span> →
       <span class="ficha ficha--int ficha--nueva">nuevo nodo <b>${datos.nodos[siguiente[2]].f}</b></span>
       <span class="tenue">(son los dos de menor frecuencia)</span>`
    : `<span class="fucsia">✔ Árbol completo:</span> queda un solo nodo, la raíz, con frecuencia <b>${miles(datos.nodos[recien]?.f ?? 0)}</b> = total de caracteres.`;

  const elegidos = siguiente ? new Set([siguiente[0], siguiente[1]]) : new Set();
  q("cola").innerHTML = ordenada.map((id) => {
    const n = datos.nodos[id];
    const clases = ["ficha", n.c === null ? "ficha--int" : "", elegidos.has(id) ? "ficha--elegida" : "", id === recien ? "ficha--nueva" : ""].join(" ");
    return `<span class="${clases}">${escaparHTML(n.c !== null ? etiquetaCorta(n.c) : "Σ")} <b>${miles(n.f)}</b></span>`;
  }).join("");

  raizVista.querySelectorAll('[data-c="tabla"] tr').forEach((tr) => {
    const activa = Number(tr.dataset.i) === paso;
    tr.classList.toggle("sel", activa);
    tr.style.background = activa ? "rgba(253,224,71,.1)" : "";
  });
  const fila = raizVista.querySelector(`[data-c="tabla"] tr[data-i="${paso}"]`);
  const caja = fila?.closest(".tabla-scroll");
  if (caja) caja.scrollTop = fila.offsetTop - caja.clientHeight / 2;
}
