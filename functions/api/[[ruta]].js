// Cloudflare Pages Functions: atiende /api/buscar y /api/libro/<id> con la
// misma lógica del Worker (worker/index.js). Así el buscador funciona tanto
// publicado como Worker (wrangler.jsonc) como en Cloudflare Pages conectado a GitHub.
import worker from "../../worker/index.js";

export function onRequest(context) {
  return worker.fetch(context.request, context.env);
}
