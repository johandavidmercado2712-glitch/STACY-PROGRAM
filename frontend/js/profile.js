import { getTokenUser, clearToken } from './auth.js';
import { fetchUserProfile } from './api.js';

let _profileData = null;

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
}

export async function actualizarPanel(forceFetch) {
  const user = getTokenUser();
  if (!user) return;

  const initial = user.charAt(0).toUpperCase();
  const avatarEl = document.getElementById("profile-avatar");
  if (avatarEl) avatarEl.textContent = initial;

  if (forceFetch || !_profileData) {
    try {
      _profileData = await fetchUserProfile();
    } catch (e) {
      _profileData = null;
    }
  }

  const data = _profileData || {};
  const name = data.username || user;
  const apellidos = data.apellidos || "";
  const correo = data.correo || "";

  const usernameEl = document.getElementById("profile-username");
  if (usernameEl) usernameEl.textContent = name;

  let bodyHtml = "";

  if (apellidos) {
    bodyHtml += '<div class="profile-field"><span class="profile-field-label">Apellidos</span><span class="profile-field-value">' + escapeHtml(apellidos) + '</span></div>';
  }
  if (correo) {
    bodyHtml += '<div class="profile-field"><span class="profile-field-label">Correo</span><span class="profile-field-value">' + escapeHtml(correo) + '</span></div>';
  }

  bodyHtml += '<hr class="profile-divider" />';

  document.querySelector(".profile-body").innerHTML = bodyHtml +
    '<button class="profile-logout" id="profile-logout">' +
      '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' +
      'Cerrar sesion' +
    '</button>';

  document.getElementById("profile-logout").addEventListener("click", function () {
    cerrarPanel();
    clearToken();
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function abrirPanel() {
  actualizarPanel(true);
  document.getElementById("profile-overlay").style.display = "block";
  document.getElementById("profile-panel").classList.add("open");
}

function cerrarPanel() {
  document.getElementById("profile-panel").classList.remove("open");
  document.getElementById("profile-overlay").style.display = "none";
}
