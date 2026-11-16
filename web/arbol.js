// Vistas del árbol de Huffman: jerárquica (SVG) y explorador (lista desplegable).
// Cada elemento lleva su camino ("0101") en data-p para resaltar el código
// de un carácter. La vista radial está en arbol_radial.js.

import { escaparHTML } from "./python.js";

const SEP_X = 50, SEP_Y = 78, RADIO_HOJA = 19, RADIO_INT = 16, MARGEN = 34;

/** Recorre el árbol y regresa [{nodo, camino, x (orden de hoja), nivel}]. */
export function posicionar(raiz) {
  const nodos = [];
  let hoja = 0;
  (function visitar(nodo, camino, nivel) {
    let x;
    if (nodo.c !== undefined) {
      x = hoja++;
    } else {
      const xs = [];
      if (nodo.i) xs.push(visitar(nodo.i, camino + "0", nivel + 1));
      if (nodo.d) xs.push(visitar(nodo.d, camino + "1", nivel + 1));
      x = xs.reduce((a, b) => a + b, 0) / xs.length;
    }
    nodos.push({ nodo, camino, x, nivel });
    return x;
  })(raiz, "", 0);
  return { nodos, hojas: hoja, altura: Math.max(...nodos.map((n) => n.nivel)) };
}

/** Texto corto para mostrar un carácter dentro de un nodo. */
export function etiquetaCorta(c) {
  return c.length > 2 ? c.split(" ")[0] : c;
}

/** SVG de aristas + nodos dadas las coordenadas de cada camino. */
export function svgArbol(nodos, coord) {
  const pos = new Map(nodos.map((n) => [n.camino, n]));
  const aristas = [], figuras = [];
  for (const n of nodos) {
    const [x, y] = coord(n);
    if (n.camino) {
      const [x1, y1] = coord(pos.get(n.camino.slice(0, -1)));
      const bit = n.camino.slice(-1);
      aristas.push(`<line class="a${bit}" data-p="${n.camino}" x1="${x1}" y1="${y1}" x2="${x}" y2="${y}"/>`);
      const mx = (x1 + x) / 2, my = (y1 + y) / 2;
      // Etiqueta desplazada perpendicularmente a la arista
      const dx = x - x1, dy = y - y1, largo = Math.hypot(dx, dy) || 1;
      const lado = bit === "0" ? -1 : 1;
      aristas.push(`<text class="b${bit}" x="${mx + (-dy / largo) * 9 * lado}" y="${my + (dx / largo) * 9 * lado + 4}" text-anchor="middle">${bit}</text>`);
    }
    if (n.nodo.c !== undefined) {
      figuras.push(
        `<g data-p="${n.camino}"><title>${escaparHTML(n.nodo.c)} · frecuencia ${n.nodo.f} · código ${n.camino || "0"}</title>` +
        `<circle class="n-hoja" cx="${x}" cy="${y}" r="${RADIO_HOJA}"/>` +
        `<text class="t-hoja" x="${x}" y="${y}" text-anchor="middle">${escaparHTML(etiquetaCorta(n.nodo.c))}</text>` +
        `<text class="t-frec" x="${x}" y="${y + 11}" text-anchor="middle">(${n.nodo.f})</text></g>`);
    } else {
      figuras.push(
        `<g><title>Nodo interno · suma ${n.nodo.f}</title><circle class="n-int" cx="${x}" cy="${y}" r="${RADIO_INT}"/>` +
        `<text class="t-int" x="${x}" y="${y + 3.5}" text-anchor="middle">${n.nodo.f}</text></g>`);
    }
  }
  return aristas.join("") + figuras.join("");
}

/** Resalta el camino de un código en cualquier vista SVG. */
export function resaltarSVG(contenedor, codigo, centro) {
  contenedor.querySelectorAll(".on").forEach((e) => e.classList.remove("on"));
  if (!codigo) return;
  for (let k = 1; k <= codigo.length; k++) {
    contenedor.querySelector(`line[data-p="${codigo.slice(0, k)}"]`)?.classList.add("on");
  }
  const hoja = contenedor.querySelector(`g[data-p="${codigo}"]`);
  if (hoja) {
    hoja.classList.add("on");
    const [x, y] = centro(codigo);
    contenedor.scrollTo({ left: x - contenedor.clientWidth / 2, top: y - contenedor.clientHeight / 2, behavior: "smooth" });
  }
}

// ------------------------------------------------------------------ jerárquico
export function dibujarJerarquico(contenedor, raiz, escala = 1) {
  const { nodos, hojas, altura } = posicionar(raiz);
  const coord = (n) => [MARGEN + RADIO_HOJA + n.x * SEP_X, MARGEN + RADIO_HOJA + n.nivel * SEP_Y];
  const ancho = MARGEN * 2 + RADIO_HOJA * 2 + (hojas - 1) * SEP_X;
  const alto = MARGEN * 2 + RADIO_HOJA * 2 + altura * SEP_Y;
  contenedor.className = "lienzo lineas";
  contenedor.innerHTML =
    `<svg width="${ancho * escala}" height="${alto * escala}" viewBox="0 0 ${ancho} ${alto}" xmlns="http://www.w3.org/2000/svg">` +
    svgArbol(nodos, coord) + "</svg>";
  const pos = new Map(nodos.map((n) => [n.camino, n]));
  contenedor.scrollLeft = coord(pos.get(""))[0] * escala - contenedor.clientWidth / 2;
  contenedor.scrollTop = 0;
  return {
    texto: `${hojas} hojas · altura ${altura}`,
    resaltar: (codigo) => resaltarSVG(contenedor, codigo, (c) => coord(pos.get(c)).map((v) => v * escala)),
  };
}

// ------------------------------------------------------------------ explorador
export function dibujarExplorador(contenedor, raiz) {
  function rama(nodo, camino, nivel) {
    const bit = camino ? `<span class="ex-bit ex-bit--${camino.slice(-1)}">${camino.slice(-1)}</span>` : "";
    if (nodo.c !== undefined) {
      return `<li><span class="ex-hoja" data-p="${camino}">${bit}<span class="ex-car">${escaparHTML(nodo.c)}</span>` +
        `<span class="tenue">frec ${nodo.f}</span><span class="ex-codigo">${camino || "0"}</span></span></li>`;
    }
    const hijos = [nodo.i && rama(nodo.i, camino + "0", nivel + 1), nodo.d && rama(nodo.d, camino + "1", nivel + 1)]
      .filter(Boolean).join("");
    const titulo = camino ? `camino ${camino}` : "raíz";
    return `<li><details data-p="${camino}"${nivel < 3 ? " open" : ""}><summary>${bit}<span class="ex-suma">Σ ${nodo.f}</span>` +
      `<span class="tenue">${titulo}</span></summary><ul>${hijos}</ul></details></li>`;
  }
  contenedor.className = "lienzo explorador";
  contenedor.innerHTML = `<ul>${rama(raiz, "", 0)}</ul>`;
  contenedor.scrollTo(0, 0);
  return {
    texto: "Haz clic en ▸ para abrir o cerrar ramas",
    resaltar(codigo) {
      contenedor.querySelectorAll(".ex-hoja.on").forEach((e) => e.classList.remove("on"));
      if (!codigo) return;
      for (let k = 0; k < codigo.length; k++) {
        const d = contenedor.querySelector(`details[data-p="${codigo.slice(0, k)}"]`);
        if (d) d.open = true;
      }
      const hoja = contenedor.querySelector(`.ex-hoja[data-p="${codigo}"]`);
      if (hoja) {
        hoja.classList.add("on");
        hoja.scrollIntoView({ block: "center", behavior: "smooth" });
      }
    },
  };
}

/** Permite mover el lienzo arrastrando con el mouse. */
export function arrastrable(contenedor) {
  let inicio = null;
  contenedor.addEventListener("mousedown", (e) => {
    if (e.target.closest("summary, input, button")) return;
    inicio = { x: e.clientX, y: e.clientY, l: contenedor.scrollLeft, t: contenedor.scrollTop };
  });
  window.addEventListener("mousemove", (e) => {
    if (!inicio) return;
    contenedor.scrollLeft = inicio.l - (e.clientX - inicio.x);
    contenedor.scrollTop = inicio.t - (e.clientY - inicio.y);
  });
  window.addEventListener("mouseup", () => { inicio = null; });
}
