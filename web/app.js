// Punto de entrada de la página: navegación e inicialización de cada sección.

import { listo, aviso } from "./python.js";
import { iniciarHuffman } from "./huffman_ui.js";
import { iniciarBuscador } from "./buscador.js";
import { iniciarMST } from "./mst_ui.js";

document.querySelectorAll(".nav-btn").forEach((boton) => {
  boton.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("activa", b === boton));
    document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("activo", p.id === boton.dataset.panel));
  });
});

iniciarHuffman();
iniciarBuscador();
iniciarMST();
listo
  .then(() => aviso("Python cargado: ya puedes buscar un libro o subir un .txt.", "ok"))
  .catch(() => aviso("No se pudo cargar Python (Pyodide). Revisa tu conexión y recarga la página.", "error"));
