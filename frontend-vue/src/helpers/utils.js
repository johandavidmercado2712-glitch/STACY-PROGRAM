export function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

export function formatearHora(fecha) {
  if (!fecha) return "";
  const d = new Date(fecha.replace(" ", "T"));
  return d.toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function extractMaquina(ruta) {
  if (!ruta) return null;
  const m = ruta.match(/^\[MAQUINA:(.*?)\]\s*/);
  return m ? m[1] : null;
}

export function limpiarRuta(ruta) {
  if (!ruta) return "";
  return ruta.replace(/^\[MAQUINA:.*?\]\s*/, "") || ruta;
}
