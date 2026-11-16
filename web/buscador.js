// Buscador de libros de Project Gutenberg (a través del Worker en /api)
// y carga de archivos propios (.txt o .mc) con arrastrar y soltar.

import { escaparHTML, miles, ocupado, aviso } from "./python.js";
import { cargarLibro, decodificarArchivoHuf } from "./huffman_ui.js";

const $ = (id) => document.getElementById(id);
let busqueda = { q: "", idioma: "", pagina: 1 };

export function iniciarBuscador() {
  $("form-buscar").addEventListener("submit", (e) => {
    e.preventDefault();
    busqueda = { q: $("q").value.trim(), idioma: $("idioma").value, pagina: 1 };
    buscar(false);
  });

  $("resultados").addEventListener("click", (e) => {
    const usar = e.target.closest("[data-id]");
    if (usar) usarLibro(usar.dataset.id, usar.dataset.titulo, usar.dataset.autor);
    if (e.target.closest("#ver-mas")) {
      busqueda.pagina += 1;
      buscar(true);
    }
  });

  // Arrastrar y soltar
  const zona = $("zona-soltar");
  zona.addEventListener("dragover", (e) => { e.preventDefault(); zona.classList.add("encima"); });
  zona.addEventListener("dragleave", () => zona.classList.remove("encima"));
  zona.addEventListener("drop", (e) => {
    e.preventDefault();
    zona.classList.remove("encima");
    if (e.dataTransfer.files.length) abrirArchivo(e.dataTransfer.files[0]);
  });
  $("archivo").addEventListener("change", (e) => {
    if (e.target.files.length) abrirArchivo(e.target.files[0]);
    e.target.value = "";
  });
}

async function abrirArchivo(archivo) {
  const bytes = new Uint8Array(await archivo.arrayBuffer());
  const nombre = archivo.name.toLowerCase();
  try {
    if (nombre.endsWith(".mc")) {
      await decodificarArchivoHuf(bytes, archivo.name);
    } else if (nombre.endsWith(".txt") || archivo.type.startsWith("text/")) {
      await cargarLibro(prepararTexto(bytes), archivo.name, "archivo propio", archivo.name);
    } else {
      aviso("Solo se aceptan archivos .txt o .mc.", "error");
    }
  } catch (error) {
    console.error(error);
    aviso("No se pudo procesar el archivo: " + error.message.split("\n").slice(-2).join(" "), "error");
  }
}

async function buscar(agregar) {
  const cont = $("resultados");
  $("ver-mas")?.closest("p")?.remove();
  if (!agregar) cont.innerHTML = `<p class="mensaje">Buscando «${escaparHTML(busqueda.q)}» en gutenberg.org…</p>`;
  try {
    const params = new URLSearchParams({ q: busqueda.q, idioma: busqueda.idioma, pagina: busqueda.pagina });
    const r = await fetch("/api/buscar?" + params);
    const datos = await r.json();
    if (!r.ok) throw new Error(datos.error || "HTTP " + r.status);
    if (!agregar) cont.innerHTML = "";
    if (!datos.libros.length && !agregar) {
      cont.innerHTML = `<p class="mensaje">No se encontraron libros. Prueba con otro título, autor o idioma.</p>`;
      return;
    }
    cont.insertAdjacentHTML("beforeend", datos.libros.map(tarjeta).join(""));
    cont.insertAdjacentHTML("beforeend",
      `<p class="mensaje">${datos.hayMas ? '<button type="button" id="ver-mas" class="btn btn--chico">Ver más resultados</button> ' : ""}` +
      `<span class="tenue">fuente: ${escaparHTML(datos.fuente)}</span></p>`);
  } catch (error) {
    cont.innerHTML = `<p class="mensaje mensaje--error">No se pudo buscar: ${escaparHTML(error.message)}.
      El buscador solo funciona con la página publicada (necesita el Worker de Cloudflare).</p>`;
  }
}

function tarjeta(libro) {
  return `<div class="libro">
    <h4>${escaparHTML(libro.titulo)}</h4>
    <p>${escaparHTML(libro.autor || "Autor desconocido")} · #${libro.id} · ${miles(libro.descargas)} descargas</p>
    <button type="button" class="btn btn--chico btn--contorno" data-id="${libro.id}"
      data-titulo="${escaparHTML(libro.titulo)}" data-autor="${escaparHTML(libro.autor || "")}">Usar</button>
  </div>`;
}

async function usarLibro(id, titulo, autor) {
  let bytes;
  try {
    bytes = await ocupado(`Descargando el libro #${id} de gutenberg.org…`, async () => {
      const r = await fetch("/api/libro/" + id);
      if (!r.ok) {
        const datos = await r.json().catch(() => ({}));
        throw new Error(datos.error || "HTTP " + r.status);
      }
      return new Uint8Array(await r.arrayBuffer());
    });
  } catch (error) {
    aviso("No se pudo descargar el libro: " + error.message, "error");
    return;
  }
  await cargarLibro(prepararTexto(bytes), titulo, [autor, "Gutenberg #" + id].filter(Boolean).join(" · "), `pg${id}_${titulo}`);
}

/** Si la casilla está marcada, quita el encabezado y la licencia de Project Gutenberg. */
function prepararTexto(bytes) {
  if (!$("quitar-licencia").checked) return bytes;
  const texto = new TextDecoder("utf-8").decode(bytes);
  const inicio = texto.search(/\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG E-?BOOK[^\n]*\n/i);
  const fin = texto.search(/\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG E-?BOOK/i);
  if (inicio < 0) return bytes;
  const desde = texto.indexOf("\n", inicio) + 1;
  return new TextEncoder().encode(texto.slice(desde, fin > desde ? fin : undefined).trim() + "\n");
}
