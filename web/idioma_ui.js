// Pestaña "Idioma": muestra el resultado del detector de idioma (idioma/detector.py).

import { escaparHTML, miles } from "./python.js";

export function montarIdioma(contenedor, idioma) {
  if (!idioma.codigo) {
    contenedor.innerHTML = `<div class="tarjeta-oscura"><h3>No se pudo identificar el idioma</h3>
      <p>El texto es muy corto o no contiene suficientes palabras comunes de los idiomas conocidos.</p></div>`;
    return;
  }
  const radio = 70, circ = 2 * Math.PI * radio;
  const relleno = (idioma.confianza / 100) * circ;
  const ganador = idioma.ranking[0][0];
  let gutenberg = "";
  if (idioma.declarado_gutenberg) {
    gutenberg = idioma.coincide_con_gutenberg
      ? `<p class="pequeno">Gutenberg declara: <b>${escaparHTML(idioma.declarado_gutenberg)}</b> <span class="fucsia">✔ coincide</span></p>`
      : `<p class="pequeno">Gutenberg declara: <b>${escaparHTML(idioma.declarado_gutenberg)}</b> <span class="rosa">✘ no coincide</span></p>`;
  }

  contenedor.innerHTML = `
    <div class="idioma">
      <div class="tarjeta-oscura idioma__principal">
        <h3><svg class="ico"><use href="#i-globo"/></svg> Idioma detectado</h3>
        <div class="anillo">
          <svg viewBox="0 0 170 170">
            <defs><linearGradient id="g-anillo" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset="1" stop-color="#a855f7"/></linearGradient></defs>
            <circle cx="85" cy="85" r="${radio}" fill="none" stroke="#1e1b2e" stroke-width="14"/>
            <circle cx="85" cy="85" r="${radio}" fill="none" stroke="url(#g-anillo)" stroke-width="14" stroke-linecap="round"
              stroke-dasharray="${relleno} ${circ}" style="filter:drop-shadow(0 0 6px rgba(217,70,239,.7))"/>
          </svg>
          <div class="anillo__centro"><strong class="degradado">${idioma.confianza.toFixed(0)}%</strong><span>CONFIANZA</span></div>
        </div>
        <div class="idioma__nombre">${escaparHTML(idioma.nombre)}</div>
        <span class="codigo-idioma">${escaparHTML(idioma.codigo)}</span>
        <p class="pequeno tenue">${miles(idioma.palabras_analizadas)} palabras analizadas ·
          ${idioma.cobertura.toFixed(1)} % son palabras comunes del ${escaparHTML(idioma.nombre.toLowerCase())}</p>
        ${gutenberg}
      </div>

      <div class="tarjeta-oscura">
        <h3><svg class="ico"><use href="#i-grafica"/></svg> Comparación entre idiomas</h3>
        <p>Puntaje de cada idioma según cuántas de sus palabras comunes aparecen en el texto.</p>
        <div class="ranking">${idioma.ranking.map(([cod, nombre, pct]) =>
          `<div class="ranking-fila ${cod === ganador ? "ranking-fila--gana" : ""}"><span>${escaparHTML(nombre)}</span>` +
          `<div class="bc-barra"><i style="width:${pct}%"></i></div><span class="bc-valor">${pct.toFixed(1)} %</span></div>`).join("")}
        </div>
        <h3 style="margin-top:6px"><svg class="ico"><use href="#i-buscar"/></svg> Palabras que lo delatan</h3>
        <div class="fichas">${idioma.palabras_clave.map(([p, n]) =>
          `<span class="ficha">${escaparHTML(p)} <b>${miles(n)}</b></span>`).join("")}</div>
        ${idioma.letras_especiales.length ? `<h3 style="margin-top:6px">Letras características</h3>
        <div class="fichas">${idioma.letras_especiales.map((l) => `<span class="ficha ficha--int"><b>${escaparHTML(l)}</b></span>`).join("")}</div>` : ""}
        <p class="pequeno tenue">Método: conteo de palabras vacías (artículos, preposiciones, conjunciones) + letras propias de cada idioma.
          Se ignora el encabezado y la licencia de Project Gutenberg, que siempre están en inglés.</p>
      </div>
    </div>`;
}
