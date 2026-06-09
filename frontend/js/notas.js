import { fetchNotas, createNota, updateNota, deleteNota } from './api.js';
import { showModal, hideModal } from './folders.js';
import { getToken } from './auth.js';

let _notas = [];
let _notaActiva = null;

export function initNotas() {
  document.getElementById("nota-new-btn").addEventListener("click", function () {
    abrirModalCreador();
  });

  if (getToken()) cargarNotas();
}

export async function cargarNotas() {
  try {
    const res = await fetchNotas();
    _notas = res.notas || [];
  } catch (e) {
    _notas = [];
  }
  renderNotas();
}

function renderNotas() {
  const container = document.getElementById("nota-list");
  if (_notas.length === 0) {
    container.innerHTML = '<div class="nota-empty">No tienes notas aun</div>';
    return;
  }
  container.innerHTML = "";
  _notas.forEach(function (n) {
    const card = document.createElement("div");
    card.className = "nota-card";
    card.dataset.id = n.NOT_ID;

    const preview = (n.NOT_CONTENIDO || "").replace(/\n/g, " ").substring(0, 80);
    const fecha = n.NOT_UPDATED_AT
      ? new Date(n.NOT_UPDATED_AT.replace(" ", "T")).toLocaleDateString("es-ES", { day: "numeric", month: "short" })
      : "";

    card.innerHTML =
      '<div class="nota-card-title">' + escapeHtml(n.NOT_TITULO || "Sin titulo") + '</div>' +
      '<div class="nota-card-preview">' + escapeHtml(preview) + '</div>' +
      '<div class="nota-card-date">' + fecha + '</div>';

    card.addEventListener("click", function () {
      abrirModalEditor(n.NOT_ID);
    });

    container.appendChild(card);
  });
}

function abrirModalCreador() {
  _notaActiva = null;
  const bodyHTML =
    '<input type="text" id="nota-title-input" class="modal-input" placeholder="Titulo de la nota" />' +
    '<textarea id="nota-content-input" class="modal-input" style="margin-top:0.5rem;min-height:200px;resize:vertical;" placeholder="Escribe tu nota aqui..."></textarea>';

  showModal("Nueva nota", bodyHTML);

  document.getElementById("modal-title-input")?.focus();
  document.getElementById("modal-save").style.display = "";
  document.getElementById("modal-save").textContent = "Guardar";
  document.getElementById("modal-save").onclick = guardarNota;
  document.getElementById("modal-cancel").style.display = "";
  document.getElementById("modal-cancel").textContent = "Cancelar";
  document.getElementById("modal-cancel").onclick = hideModal;
  document.getElementById("modal-close").onclick = hideModal;
  document.getElementById("modal-overlay").onclick = function (e) {
    if (e.target === this) hideModal();
  };
}

function abrirModalEditor(notId) {
  const nota = _notas.find(function (n) { return n.NOT_ID === notId; });
  if (!nota) return;
  _notaActiva = nota;

  const bodyHTML =
    '<input type="text" id="nota-title-input" class="modal-input" placeholder="Titulo de la nota" value="' + escapeHtml(nota.NOT_TITULO || "") + '" />' +
    '<textarea id="nota-content-input" class="modal-input" style="margin-top:0.5rem;min-height:200px;resize:vertical;" placeholder="Escribe tu nota aqui...">' + escapeHtml(nota.NOT_CONTENIDO || "") + '</textarea>';

  showModal("Editar nota", bodyHTML);

  document.getElementById("nota-title-input").focus();
  document.getElementById("modal-save").style.display = "";
  document.getElementById("modal-save").textContent = "Guardar";
  document.getElementById("modal-save").onclick = guardarNota;
  document.getElementById("modal-cancel").style.display = "";
  document.getElementById("modal-cancel").textContent = "Cancelar";
  document.getElementById("modal-cancel").onclick = hideModal;
  document.getElementById("modal-close").onclick = hideModal;
  document.getElementById("modal-overlay").onclick = function (e) {
    if (e.target === this) hideModal();
  };

  const footer = document.getElementById("modal-footer");
  let deleteBtn = document.getElementById("nota-modal-delete");
  if (!deleteBtn) {
    deleteBtn = document.createElement("button");
    deleteBtn.id = "nota-modal-delete";
    deleteBtn.className = "btn-sm btn-outline";
    deleteBtn.textContent = "Eliminar";
    deleteBtn.style.color = "var(--danger)";
    deleteBtn.style.borderColor = "rgba(248,81,73,0.3)";
    footer.insertBefore(deleteBtn, footer.firstChild);
  }
  deleteBtn.style.display = "";
  deleteBtn.onclick = async function () {
    if (!confirm("¿Eliminar esta nota?")) return;
    try {
      await deleteNota(nota.NOT_ID);
      _notaActiva = null;
      hideModal();
      await cargarNotas();
    } catch (e) {
      console.error("Error al eliminar nota:", e);
    }
  };
}

async function guardarNota() {
  const titulo = document.getElementById("nota-title-input").value.trim();
  const contenido = document.getElementById("nota-content-input").value;

  if (!titulo) {
    document.getElementById("nota-title-input").focus();
    return;
  }

  try {
    if (_notaActiva) {
      await updateNota(_notaActiva.NOT_ID, titulo, contenido);
    } else {
      await createNota(titulo, contenido);
    }
    hideModal();
    await cargarNotas();
  } catch (e) {
    console.error("Error al guardar nota:", e);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
