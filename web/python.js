// Carga Pyodide (Python en WebAssembly) y los módulos del proyecto.
// Los algoritmos están en Python; aquí solo se pasan datos entre JS y Python.

const ARCHIVOS = [
  "huffman/__init__.py", "huffman/frecuencias.py", "huffman/arbol.py", "huffman/codigos.py",
  "huffman/codificador.py", "huffman/estadisticas.py",
  "mst/__init__.py", "mst/grafo.py", "mst/kruskal.py", "mst/prim.py",
  "idioma/__init__.py", "idioma/detector.py",
  "web/puente.py",
];

export const CARPETA = "/tmp/huffman_web";
let pyodide = null;

export const listo = (async () => {
  const estado = document.getElementById("estado-python");
  try {
    pyodide = await loadPyodide();
    for (const ruta of ARCHIVOS) {
      const r = await fetch(ruta, { cache: "no-cache" });
      if (!r.ok) throw new Error("No se pudo cargar " + ruta);
      const destino = "/proyecto/" + ruta.replace(/^web\//, "");
      pyodide.FS.mkdirTree(destino.slice(0, destino.lastIndexOf("/")));
      pyodide.FS.writeFile(destino, await r.text());
    }
    pyodide.runPython("import sys\nsys.path.insert(0, '/proyecto')\nimport puente");
    estado.innerHTML = '<i class="punto"></i>PYTHON LISTO';
    estado.className = "estado estado--lista";
    document.dispatchEvent(new Event("python-listo"));
  } catch (error) {
    estado.innerHTML = '<i class="punto"></i>ERROR AL CARGAR PYTHON';
    estado.className = "estado estado--error";
    console.error(error);
    throw error;
  }
})();

/** Ejecuta una función de puente.py y regresa su resultado (JSON) ya convertido. */
export function py(llamada) {
  return JSON.parse(pyodide.runPython("puente." + llamada));
}

export function escribir(ruta, bytes) {
  pyodide.FS.writeFile(ruta, bytes);
}

export function leer(ruta) {
  return pyodide.FS.readFile(ruta);
}

export function borrar(ruta) {
  try { pyodide.FS.unlink(ruta); } catch (e) { /* no existía */ }
}

/** Muestra la cubierta "Procesando…" mientras corre una tarea pesada. */
export async function ocupado(texto, tarea) {
  const cubierta = document.getElementById("cubierta");
  document.getElementById("cubierta-texto").textContent = texto;
  cubierta.classList.remove("oculto");
  // Dar tiempo al navegador de pintar la cubierta antes de bloquear con Python
  // (setTimeout y no requestAnimationFrame: este último nunca se dispara si la pestaña está en segundo plano)
  await new Promise((r) => setTimeout(r, 50));
  try {
    await listo;
    return await tarea();
  } finally {
    cubierta.classList.add("oculto");
  }
}

export function formatoBytes(n) {
  if (n < 1024) return Math.round(n) + " B";
  if (n < 1024 * 1024) return (n / 1024).toFixed(2) + " KB";
  return (n / 1024 / 1024).toFixed(2) + " MB";
}

export const miles = (n) => Number(n).toLocaleString("es-MX");

export function descargar(bytes, nombre, tipo) {
  const url = URL.createObjectURL(new Blob([bytes], { type: tipo }));
  const a = Object.assign(document.createElement("a"), { href: url, download: nombre });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

export function escaparHTML(texto) {
  return String(texto).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/** Notificación flotante (tipo: "info", "ok" o "error"). */
export function aviso(mensaje, tipo = "info") {
  const icono = { info: "i-info", ok: "i-ok", error: "i-x" }[tipo] || "i-info";
  const caja = document.createElement("div");
  caja.className = "aviso aviso--" + tipo;
  caja.innerHTML = `<svg class="ico"><use href="#${icono}"/></svg><span>${escaparHTML(mensaje)}</span>`;
  document.getElementById("avisos").appendChild(caja);
  setTimeout(() => caja.classList.add("visible"), 20);
  setTimeout(() => {
    caja.classList.remove("visible");
    setTimeout(() => caja.remove(), 300);
  }, 4000);
}
