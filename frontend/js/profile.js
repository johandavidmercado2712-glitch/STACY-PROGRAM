import { getTokenUser, clearToken } from './auth.js';

export function initProfile() {
  const userLabel = document.getElementById("user-label");
  const profilePanel = document.getElementById("profile-panel");
  const profileOverlay = document.getElementById("profile-overlay");

  if (!userLabel || !profilePanel || !profileOverlay) return;

  userLabel.addEventListener("click", function (e) {
    e.stopPropagation();
    abrirPanel();
  });

  profileOverlay.addEventListener("click", function (e) {
    if (e.target === profileOverlay) cerrarPanel();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") cerrarPanel();
  });

  document.getElementById("profile-logout").addEventListener("click", function () {
    cerrarPanel();
    clearToken();
  });
}

export function actualizarPanel() {
  const user = getTokenUser();
  if (!user) return;

  document.getElementById("profile-username").textContent = user;
  const initial = user.charAt(0).toUpperCase();
  document.getElementById("profile-avatar").textContent = initial;
}

function abrirPanel() {
  actualizarPanel();
  document.getElementById("profile-overlay").style.display = "block";
  document.getElementById("profile-panel").classList.add("open");
}

function cerrarPanel() {
  document.getElementById("profile-panel").classList.remove("open");
  document.getElementById("profile-overlay").style.display = "none";
}
