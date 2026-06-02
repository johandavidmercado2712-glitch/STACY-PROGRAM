import { state } from './state.js';
import { fetchComandos, assignCommandApi, unassignCommandApi, updateCommandDescription } from './api.js';
import { getToken } from './auth.js';
import { setCommandFolders, loadFolders, renderFolders, showModal, hideModal } from './folders.js';

let _onCommandsLoaded = null;

export function onCommandsLoaded(callback) {
  _onCommandsLoaded = callback;
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function formatearHora(fechaTexto) {
  if (!fechaTexto) return "--:--";
  const fecha = new Date(fechaTexto.replace(" ", "T"));
  if (Number.isNaN(fecha.getTime())) return "--:--";
  return fecha.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
}

function getFolderNames(comId) {
  const ids = state.commandFolders[comId] || [];
  return ids.map(function (id) {
    const found = state.folders.find(function (f) { return f.CAR_ID === id; });
    return found ? found.CAR_NOMBRE : null;
  }).filter(Boolean);
}

function crearItemComando(item, folderView) {
  const li = document.createElement("li");
  const comId = item.com_id;

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = formatearHora(item.fecha);

  const code = document.createElement("code");
  code.textContent = item.comando || "(sin comando)";

  const path = document.createElement("span");
  path.className = "path";
  path.textContent = item.ruta || "(sin ruta)";

  li.appendChild(time);
  li.appendChild(code);
  li.appendChild(path);

  if (folderView) {
    const btnGroup = document.createElement("div");
    btnGroup.style.cssText = "display:flex;gap:0.3rem;";

    const detallesBtn = document.createElement("button");
    detallesBtn.className = "btn-folder-action";
    detallesBtn.textContent = "Detalles";

    const descKey = state.selectedFolderId + "_" + comId;
    detallesBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      showModal("Detalles del comando",
        '<div class="detail-field">' +
          '<span class="detail-label">Comando</span>' +
          '<code class="detail-code">' + escapeHtml(item.comando || "") + '</code>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Ruta</span>' +
          '<span class="detail-value">' + escapeHtml(item.ruta || "") + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Hora</span>' +
          '<span class="detail-value">' + formatearHora(item.fecha) + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Carpetas</span>' +
          '<span class="detail-value">' + escapeHtml(getFolderNames(comId).join(", ") || "Ninguna") + '</span>' +
        '</div>' +
        '<div class="detail-field" style="margin-bottom:0;">' +
          '<span class="detail-label">Nota</span>' +
          '<input id="detail-desc-input" type="text" placeholder="Agregar descripcion..." value="' + escapeHtml(state.commandDescriptions[descKey] || "") + '" class="modal-input" />' +
        '</div>'
      );

      document.getElementById("modal-save").onclick = async function () {
        const newDesc = document.getElementById("detail-desc-input").value;
        state.commandDescriptions[descKey] = newDesc;
        try {
          await updateCommandDescription(state.selectedFolderId, comId, newDesc);
        } catch (err) {
          console.error("Error al guardar descripcion:", err);
        }
        hideModal();
      };
      document.getElementById("modal-cancel").onclick = hideModal;
      document.getElementById("modal-close").onclick = hideModal;
      document.getElementById("modal-overlay").onclick = function (e) {
        if (e.target === this) hideModal();
      };
    });

    const removeBtn = document.createElement("button");
    removeBtn.className = "btn-folder-action btn-folder-action--danger";
    removeBtn.textContent = "Quitar";
    removeBtn.addEventListener("click", async function (e) {
      e.stopPropagation();
      try {
        await unassignCommandApi(state.selectedFolderId, comId);
        await loadFolders();
        renderFolders();
        renderComandos();
      } catch (err) {
        console.error("Error al quitar comando:", err);
      }
    });

    btnGroup.appendChild(detallesBtn);
    btnGroup.appendChild(removeBtn);
    li.appendChild(btnGroup);
  } else {
    const folderBadge = document.createElement("span");
    folderBadge.className = "cmd-folder-badge";
    const names = getFolderNames(comId);
    if (names.length > 0) {
      folderBadge.textContent = names.join(", ");
    } else {
      folderBadge.textContent = "Sin carpeta";
      folderBadge.classList.add("cmd-folder-badge--none");
    }

    folderBadge.addEventListener("click", function (e) {
      e.stopPropagation();
      let html = '<div class="folder-checkbox-list">';
      state.folders.forEach(function (f) {
        const checked = (state.commandFolders[comId] || []).includes(f.CAR_ID);
        html += '<label class="folder-checkbox-label">' +
          '<input type="checkbox" value="' + f.CAR_ID + '" ' + (checked ? "checked" : "") + ' class="folder-checkbox" />' +
          '<span>' + escapeHtml(f.CAR_NOMBRE) + '</span>' +
        '</label>';
      });
      html += '</div>';

      showModal("Asignar a carpetas", html);

      document.getElementById("modal-save").onclick = async function () {
        const checked = [];
        document.querySelectorAll(".folder-checkbox-list input[type=checkbox]:checked").forEach(function (cb) {
          checked.push(parseInt(cb.value));
        });
        await setCommandFolders(comId, checked);
        renderComandos();
        hideModal();
      };
      document.getElementById("modal-cancel").onclick = hideModal;
      document.getElementById("modal-close").onclick = hideModal;
      document.getElementById("modal-overlay").onclick = function (e) {
        if (e.target === this) hideModal();
      };
    });

    li.appendChild(folderBadge);
  }

  return li;
}

function renderAddCommandBar(folderId) {
  const existingBar = document.getElementById("add-command-bar");
  if (existingBar) existingBar.remove();

  const statusMessage = document.getElementById("status-message");
  const bar = document.createElement("div");
  bar.id = "add-command-bar";
  bar.className = "add-command-bar";

  const label = document.createElement("div");
  label.className = "add-command-label";
  label.textContent = "Agregar comando a esta carpeta";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Buscar comando...";
  input.className = "add-command-input";

  const results = document.createElement("div");
  results.id = "add-command-results";
  results.className = "add-command-results";

  input.addEventListener("input", function () {
    const q = input.value.trim().toLowerCase();
    if (!q) {
      results.innerHTML = "";
      results.style.display = "none";
      return;
    }
    const pool = state.vistaActual === "recent" ? state.comandosCache.slice(0, 11) : state.comandosCache;
    const available = pool.filter(function (c) {
      const ids = state.commandFolders[c.com_id] || [];
      return !ids.includes(folderId) && c.com_id &&
        ((c.comando || "").toLowerCase().includes(q) || (c.ruta || "").toLowerCase().includes(q));
    }).slice(0, 30);

    results.innerHTML = "";
    if (available.length === 0) {
      results.style.display = "none";
      return;
    }
    results.style.display = "block";

    available.forEach(function (c) {
      const item = document.createElement("div");
      item.className = "add-command-result";
      item.addEventListener("click", async function () {
        await assignCommandApi(folderId, c.com_id);
        await loadFolders();
        renderFolders();
        renderComandos();
      });

      const cmd = document.createElement("code");
      cmd.className = "add-command-result-code";
      cmd.textContent = c.comando;

      const p = document.createElement("span");
      p.className = "add-command-result-path";
      p.textContent = c.ruta;

      item.appendChild(cmd);
      item.appendChild(p);
      results.appendChild(item);
    });
  });

  bar.appendChild(label);
  bar.appendChild(input);
  bar.appendChild(results);
  statusMessage.parentNode.insertBefore(bar, statusMessage);
}

export function renderComandos() {
  const commandList = document.getElementById("command-list");
  const statusMessage = document.getElementById("status-message");
  const folderBadge = document.getElementById("folder-badge");
  const panelTitle = document.getElementById("panel-title");

  commandList.innerHTML = "";

  const existingBar = document.getElementById("add-command-bar");
  if (existingBar) existingBar.remove();

  const pool = state.vistaActual === "recent" ? state.comandosCache.slice(0, 11) : state.comandosCache;
  let filtered = pool;

  if (state.selectedFolderId === "uncategorized") {
    filtered = pool.filter(function (c) {
      const ids = state.commandFolders[c.com_id];
      return !ids || ids.length === 0;
    });
  } else if (state.selectedFolderId !== "all") {
    filtered = pool.filter(function (c) {
      const ids = state.commandFolders[c.com_id] || [];
      return ids.includes(state.selectedFolderId);
    });
  }

  let folderName = "";
  if (state.selectedFolderId === "uncategorized") {
    folderName = "Sin carpeta";
  } else if (state.selectedFolderId !== "all") {
    const found = state.folders.find(function (f) { return f.CAR_ID === state.selectedFolderId; });
    if (found) folderName = found.CAR_NOMBRE;
  }

  if (folderName) {
    folderBadge.textContent = folderName;
    folderBadge.style.display = "inline";
  } else {
    folderBadge.style.display = "none";
  }

  const isFolderView = state.selectedFolderId !== "all" && state.selectedFolderId !== "uncategorized";
  if (isFolderView) {
    renderAddCommandBar(state.selectedFolderId);
  }

  if (!Array.isArray(filtered) || filtered.length === 0) {
    statusMessage.textContent = folderName ? "Sin comandos en " + folderName + "." : "Sin comandos disponibles.";
    return;
  }

  statusMessage.textContent = "Mostrando " + filtered.length + " comando" + (filtered.length !== 1 ? "s" : "");
  filtered.forEach(function (item) {
    commandList.appendChild(crearItemComando(item, isFolderView));
  });
}

export function filtrarComandos(texto) {
  if (!texto) {
    renderComandos();
    return;
  }
  const filtrados = state.comandosCache.filter(function (item) {
    const comando = (item.comando || "").toLowerCase();
    const ruta = (item.ruta || "").toLowerCase();
    const q = texto.toLowerCase();
    return comando.includes(q) || ruta.includes(q);
  });
  const original = state.comandosCache;
  state.comandosCache = filtrados;
  renderComandos();
  state.comandosCache = original;
}

export async function cargarComandos() {
  const statusMessage = document.getElementById("status-message");
  const refreshBtn = document.getElementById("refresh-btn");
  const searchInput = document.getElementById("search-input");

  statusMessage.textContent = "Cargando comandos...";
  statusMessage.classList.remove("error");
  refreshBtn.disabled = true;

  try {
    const respuesta = await fetchComandos();
    const raw = respuesta.comandos || [];
    const seen = new Set();
    state.comandosCache = raw.filter(function (c) {
      if (!c.com_id || seen.has(c.com_id)) return false;
      seen.add(c.com_id);
      return true;
    });
    searchInput.value = "";
    renderComandos();
    if (_onCommandsLoaded) _onCommandsLoaded();
  } catch (error) {
    document.getElementById("command-list").innerHTML = "";
    state.comandosCache = [];
    statusMessage.textContent = "No se pudo conectar al backend.";
    statusMessage.classList.add("error");
  } finally {
    refreshBtn.disabled = false;
  }
}

export function setVista(vista) {
  state.vistaActual = vista;
  document.getElementById("view-recent").classList.toggle("active", vista === "recent");
  document.getElementById("view-all").classList.toggle("active", vista === "all");
  document.getElementById("panel-title").textContent = vista === "recent" ? "Ultimos comandos" : "Todos los comandos";
  renderComandos();
}

export function initCommands() {
  const refreshBtn = document.getElementById("refresh-btn");
  const searchInput = document.getElementById("search-input");
  const viewRecent = document.getElementById("view-recent");
  const viewAll = document.getElementById("view-all");

  refreshBtn.addEventListener("click", cargarComandos);

  searchInput.addEventListener("input", function (e) {
    filtrarComandos(e.target.value);
  });

  viewRecent.addEventListener("click", function () {
    if (state.vistaActual !== "recent") setVista("recent");
  });

  viewAll.addEventListener("click", function () {
    if (state.vistaActual !== "all") setVista("all");
  });

  if (getToken()) cargarComandos();
}
