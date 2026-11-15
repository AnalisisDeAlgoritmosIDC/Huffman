// Vista radial del árbol de Huffman: la raíz al centro y cada nivel en un
// círculo más grande. Las hojas se reparten alrededor según su orden, así que
// los caracteres frecuentes (códigos cortos) quedan cerca del centro.

import { posicionar, svgArbol, resaltarSVG } from "./arbol.js";

const PASO_RADIO = 58, MARGEN = 50;

export function dibujarRadial(contenedor, raiz, escala = 1) {
  const { nodos, hojas, altura } = posicionar(raiz);
  // Radio mínimo para que las hojas del último nivel no se encimen
  const paso = Math.max(PASO_RADIO, (hojas * 44) / (2 * Math.PI * Math.max(1, altura)));
  const R = altura * paso;
  const centro = R + MARGEN;
  const coord = (n) => {
    if (!n.camino) return [centro, centro];
    const angulo = (2 * Math.PI * (n.x + 0.5)) / hojas - Math.PI / 2;
    const r = n.nivel * paso;
    return [centro + r * Math.cos(angulo), centro + r * Math.sin(angulo)];
  };
  const lado = centro * 2;

  let guias = "";
  for (let nivel = 1; nivel <= altura; nivel++) {
    guias += `<circle cx="${centro}" cy="${centro}" r="${nivel * paso}" fill="none" stroke="rgba(168,85,247,.12)" stroke-dasharray="3 5"/>`;
    guias += `<text x="${centro + 4}" y="${centro - nivel * paso - 4}" fill="rgba(249,168,212,.35)" font-size="9" font-family="Fira Code, monospace">${nivel} bit${nivel > 1 ? "s" : ""}</text>`;
  }

  contenedor.className = "lienzo lineas";
  contenedor.innerHTML =
    `<svg width="${lado * escala}" height="${lado * escala}" viewBox="0 0 ${lado} ${lado}" xmlns="http://www.w3.org/2000/svg">` +
    guias + svgArbol(nodos, coord) + "</svg>";
  contenedor.scrollLeft = centro * escala - contenedor.clientWidth / 2;
  contenedor.scrollTop = centro * escala - contenedor.clientHeight / 2;

  const pos = new Map(nodos.map((n) => [n.camino, n]));
  return {
    texto: `cada círculo = 1 bit más de código · ${hojas} hojas`,
    resaltar: (codigo) => resaltarSVG(contenedor, codigo, (c) => coord(pos.get(c)).map((v) => v * escala)),
  };
}
