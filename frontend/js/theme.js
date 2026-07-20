const STORAGE_KEY = "stacy_theme";

const moonSVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
const sunSVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

export function getTheme() {
  return document.documentElement.getAttribute("data-theme") || "dark";
}

export function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(STORAGE_KEY, theme);
  updateToggleIcon();
}

export function toggleTheme() {
  const next = getTheme() === "light" ? "dark" : "light";
  setTheme(next);
}

function updateToggleIcon() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.innerHTML = getTheme() === "light" ? moonSVG : sunSVG;
  btn.title = getTheme() === "light" ? "Modo oscuro" : "Modo claro";
}

export function initTheme() {
  const saved = localStorage.getItem("stacy_theme");
  const prefers = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", saved || prefers);
  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.addEventListener("click", toggleTheme);
    updateToggleIcon();
  }
}
