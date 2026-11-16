// Barra de flujo: BUSCAR/SUBIR → ANALIZAR → CONSTRUIR → COMPRIMIR → INSPECCIONAR → DESCOMPRIMIR.
// Marca los pasos completados y permite saltar a cada uno con un clic.

const $ = (id) => document.getElementById(id);

export function iniciarFlujo() {
  marcarHasta(0);
  $("flujo").addEventListener("click", (e) => {
    const paso = Number(e.target.closest("li[data-paso]")?.dataset.paso);
    if (!paso) return;
    if (paso <= 4) irAPanel("panel-huffman");
    if (paso === 1) { $("q").focus(); $("q").scrollIntoView({ block: "center", behavior: "smooth" }); }
    if (paso === 2) document.querySelector('[data-sub="sub-tabla"]').click();
    if (paso === 3) document.querySelector('[data-sub="sub-arbol"]').click();
    if (paso === 4) { $("btn-codificar").focus(); $("btn-codificar").scrollIntoView({ block: "center", behavior: "smooth" }); }
    if (paso === 5) {
      if (!$("insp-usar-actual").disabled) $("insp-usar-actual").click();
      else irAPanel("panel-inspector");
    }
    if (paso === 6) { irAPanel("panel-inspector"); $("insp-descomprimir").focus(); }
  });
}

/** Marca como hechos los pasos 1..n y como actual el n+1. */
export function marcarHasta(n) {
  document.querySelectorAll("#flujo li").forEach((li) => {
    const paso = Number(li.dataset.paso);
    li.className = paso <= n ? "hecho" : paso === n + 1 ? "actual" : "";
  });
}

export function irAPanel(id) {
  document.querySelector(`.nav-btn[data-panel="${id}"]`)?.click();
}
