/**
 * Cloudflare Worker del proyecto.
 *
 * - Sirve la página (index.html, web/, huffman/, mst/) como archivos estáticos.
 * - /api/buscar?q=...&idioma=es&pagina=1  -> busca libros en gutenberg.org
 * - /api/libro/<id>                        -> descarga el .txt del libro desde gutenberg.org
 *
 * Hace falta este intermediario porque gutenberg.org no permite que una página
 * de otro dominio lea sus respuestas desde el navegador (CORS).
 */

const GUTENBERG = "https://www.gutenberg.org";
const GUTENDEX = "https://gutendex.com/books/"; // respaldo si la búsqueda directa falla
const POR_PAGINA = 25;
const CABECERAS = { "User-Agent": "Mozilla/5.0 (proyecto escolar Huffman; +https://www.gutenberg.org)" };

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname === "/api/buscar") return await buscar(url);
      const libro = url.pathname.match(/^\/api\/libro\/(\d+)$/);
      if (libro) return await descargarLibro(libro[1]);
      if (url.pathname.startsWith("/api/")) return json({ error: "Ruta no encontrada" }, 404);
    } catch (error) {
      return json({ error: "Error al contactar a Project Gutenberg: " + error.message }, 502);
    }
    return env.ASSETS.fetch(request);
  },
};

// ------------------------------------------------------------------ búsqueda
async function buscar(url) {
  const q = (url.searchParams.get("q") || "").trim();
  const idioma = (url.searchParams.get("idioma") || "").trim();
  const pagina = Math.max(1, parseInt(url.searchParams.get("pagina") || "1", 10));
  if (!q) return json({ error: "Escribe un título o autor" }, 400);

  let resultado = null;
  try {
    resultado = await buscarEnGutenberg(q, idioma, pagina);
  } catch (e) {
    resultado = null;
  }
  // Si la página de Gutenberg cambió de formato o no respondió, se usa Gutendex
  if (!resultado || (resultado.libros.length === 0 && pagina === 1)) {
    try {
      const respaldo = await buscarEnGutendex(q, idioma, pagina);
      if (respaldo.libros.length || !resultado) resultado = respaldo;
    } catch (e) {
      if (!resultado) throw e;
    }
  }
  return json(resultado, 200, 3600);
}

/** Búsqueda directa en https://www.gutenberg.org/ebooks/search/ */
async function buscarEnGutenberg(q, idioma, pagina) {
  // Gutenberg acepta filtros en la consulta: "l.es" = idioma español
  const consulta = idioma ? `${q} l.${idioma}` : q;
  const destino = new URL(GUTENBERG + "/ebooks/search/");
  destino.searchParams.set("query", consulta);
  destino.searchParams.set("submit_search", "Go!");
  if (pagina > 1) destino.searchParams.set("start_index", String((pagina - 1) * POR_PAGINA + 1));

  const r = await fetch(destino, { headers: CABECERAS, cf: { cacheTtl: 3600, cacheEverything: true } });
  if (!r.ok) throw new Error("HTTP " + r.status);
  const html = await r.text();
  const libros = extraerResultados(html);
  const hayMas = /rel="next"|title="Go to the next page/i.test(html) || /start_index=\d+[^"]*"[^>]*>\s*Next/i.test(html);
  return { fuente: "gutenberg.org", pagina, hayMas, libros };
}

/** Extrae los resultados del HTML de la búsqueda de Gutenberg. */
export function extraerResultados(html) {
  const libros = [];
  const bloques = html.split(/<li[^>]*class="[^"]*booklink[^"]*"[^>]*>/i).slice(1);
  for (const bloque of bloques) {
    const cuerpo = bloque.split(/<\/li>/i)[0];
    const id = (cuerpo.match(/href="\/ebooks\/(\d+)/) || [])[1];
    if (!id) continue;
    libros.push({
      id: Number(id),
      titulo: limpiar(span(cuerpo, "title")) || "Libro " + id,
      autor: limpiar(span(cuerpo, "subtitle")),
      descargas: parseInt((limpiar(span(cuerpo, "extra")).match(/[\d,]+/) || ["0"])[0].replace(/,/g, ""), 10) || 0,
    });
  }
  return libros;
}

/** Respaldo: API pública Gutendex (catálogo de Project Gutenberg en JSON). */
async function buscarEnGutendex(q, idioma, pagina) {
  const destino = new URL(GUTENDEX);
  destino.searchParams.set("search", q);
  if (idioma) destino.searchParams.set("languages", idioma);
  if (pagina > 1) destino.searchParams.set("page", String(pagina));
  const r = await fetch(destino, { headers: CABECERAS, cf: { cacheTtl: 3600, cacheEverything: true } });
  if (!r.ok) throw new Error("HTTP " + r.status);
  const datos = await r.json();
  const libros = (datos.results || [])
    .filter((l) => Object.keys(l.formats || {}).some((f) => f.startsWith("text/plain")))
    .map((l) => ({
      id: l.id,
      titulo: l.title,
      autor: (l.authors || []).map((a) => a.name).join("; "),
      descargas: l.download_count || 0,
    }));
  return { fuente: "gutendex.com (catálogo de Gutenberg)", pagina, hayMas: Boolean(datos.next), libros };
}

// ------------------------------------------------------------------ descarga
async function descargarLibro(id) {
  const candidatos = [
    `${GUTENBERG}/cache/epub/${id}/pg${id}.txt`,
    `${GUTENBERG}/ebooks/${id}.txt.utf-8`,
    `${GUTENBERG}/files/${id}/${id}-0.txt`,
  ];
  for (const destino of candidatos) {
    const r = await fetch(destino, { headers: CABECERAS, cf: { cacheTtl: 86400, cacheEverything: true } });
    const tipo = r.headers.get("content-type") || "";
    if (r.ok && !tipo.includes("text/html")) {
      return new Response(r.body, {
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "Cache-Control": "public, max-age=86400",
          "X-Origen": destino,
        },
      });
    }
  }
  return json({ error: `El libro #${id} no tiene versión en texto plano (.txt) en Gutenberg` }, 404);
}

// ------------------------------------------------------------------ utilidades
function span(html, clase) {
  const m = html.match(new RegExp(`<span[^>]*class="[^"]*\\b${clase}\\b[^"]*"[^>]*>([\\s\\S]*?)</span>`, "i"));
  return m ? m[1] : "";
}

function limpiar(texto) {
  return texto
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&#x27;/g, "'")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/\s+/g, " ")
    .trim();
}

function json(datos, estado = 200, cache = 0) {
  return new Response(JSON.stringify(datos), {
    status: estado,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": cache ? `public, max-age=${cache}` : "no-store",
    },
  });
}
