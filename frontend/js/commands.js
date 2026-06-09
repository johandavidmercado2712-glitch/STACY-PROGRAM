import { state } from './state.js';
import { fetchComandos, assignCommandApi, unassignCommandApi, updateCommandDescription } from './api.js';
import { getToken } from './auth.js';
import { setCommandFolders, loadFolders, renderFolders, showModal, hideModal } from './folders.js';
import { setCookie, getCookie } from './cookie.js';

let _onCommandsLoaded = null;

export function onCommandsLoaded(callback) {
  _onCommandsLoaded = callback;
}

const MAQ_COOKIE = "stacy_maquina";

function extractMaquina(ruta) {
  if (!ruta) return null;
  const m = ruta.match(/^\[MAQUINA:(.*?)\]\s*/);
  return m ? m[1] : null;
}

function limpiarRuta(ruta) {
  if (!ruta) return "";
  const limpia = ruta.replace(/^\[MAQUINA:.*?\]\s*/, "");
  return limpia || ruta;
}

function detectarMaquinas(comandos) {
  const set = new Set();
  comandos.forEach(function (c) {
    const m = extractMaquina(c.ruta);
    if (m) set.add(m);
  });
  return Array.from(set).sort();
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
  const maq = extractMaquina(item.ruta);

  const top = document.createElement("div");
  top.className = "cmd-top";

  const meta = document.createElement("div");
  meta.className = "cmd-meta";

  const badge = document.createElement("span");
  badge.className = "cmd-maquina-badge";
  badge.textContent = maq || "Servidor";

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = formatearHora(item.fecha);

  meta.appendChild(badge);
  meta.appendChild(time);

  const code = document.createElement("code");
  code.textContent = item.comando || "(sin comando)";

  top.appendChild(meta);
  top.appendChild(code);

  const path = document.createElement("span");
  path.className = "path";
  path.textContent = limpiarRuta(item.ruta) || "(sin ruta)";

  li.appendChild(top);
  li.appendChild(path);

  li.addEventListener("click", function (e) {
    if (window.innerWidth <= 768) {
      e.stopPropagation();
      const maq = extractMaquina(item.ruta);
      const rutaLimpia = limpiarRuta(item.ruta);
      showModal("Detalles del comando",
        '<div class="detail-field">' +
          '<span class="detail-label">Comando</span>' +
          '<code class="detail-code">' + escapeHtml(item.comando || "") + '</code>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Maquina</span>' +
          '<span class="detail-value detail-maquina">' + escapeHtml(maq || "Servidor") + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Hora</span>' +
          '<span class="detail-value">' + formatearHora(item.fecha) + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Ruta</span>' +
          '<span class="detail-value detail-path">' + escapeHtml(rutaLimpia) + '</span>' +
        '</div>' +
        (maq && rutaLimpia !== item.ruta ? '<div class="detail-field">' +
          '<span class="detail-label">Ruta completa</span>' +
          '<span class="detail-value detail-path" style="font-size:0.78rem;opacity:0.7;">' + escapeHtml(item.ruta) + '</span>' +
        '</div>' : '') +
        '<div class="detail-field">' +
          '<span class="detail-label">Carpetas</span>' +
          '<span class="detail-value">' + escapeHtml(getFolderNames(comId).join(", ") || "Ninguna") + '</span>' +
        '</div>'
      );
      document.getElementById("modal-save").style.display = "none";
      document.getElementById("modal-cancel").textContent = "Cerrar";
      document.getElementById("modal-cancel").onclick = hideModal;
      document.getElementById("modal-close").onclick = hideModal;
      document.getElementById("modal-overlay").onclick = function (e) {
        if (e.target === this) hideModal();
      };
    }
  });

  if (folderView) {
    const btnGroup = document.createElement("div");
    btnGroup.className = "cmd-actions";

    const detallesBtn = document.createElement("button");
    detallesBtn.className = "btn-folder-action";
    detallesBtn.textContent = "Detalles";

    const descKey = state.selectedFolderId + "_" + comId;
    detallesBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      const maq = extractMaquina(item.ruta);
      const rutaLimpia = limpiarRuta(item.ruta);
      showModal("Detalles del comando",
        '<div class="detail-field">' +
          '<span class="detail-label">Comando</span>' +
          '<code class="detail-code">' + escapeHtml(item.comando || "") + '</code>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Maquina</span>' +
          '<span class="detail-value detail-maquina">' + escapeHtml(maq || "Servidor") + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Hora</span>' +
          '<span class="detail-value">' + formatearHora(item.fecha) + '</span>' +
        '</div>' +
        '<div class="detail-field">' +
          '<span class="detail-label">Ruta</span>' +
          '<span class="detail-value detail-path">' + escapeHtml(rutaLimpia) + '</span>' +
        '</div>' +
        (maq && rutaLimpia !== item.ruta ? '<div class="detail-field">' +
          '<span class="detail-label">Ruta completa</span>' +
          '<span class="detail-value detail-path" style="font-size:0.78rem;opacity:0.7;">' + escapeHtml(item.ruta) + '</span>' +
        '</div>' : '') +
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

    top.appendChild(folderBadge);
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

function renderMachineFilter() {
  const container = document.getElementById("machine-filter");
  const maquinas = state.maquinasDisponibles || [];
  if (!container) return;
  if (maquinas.length === 0) {
    container.style.display = "none";
    return;
  }
  container.style.display = "";
  const active = state.selectedMaquina || "all";
  const label = active === "all" ? "Todas" : active;
  container.innerHTML = '<button class="btn-machine-select" id="machine-filter-btn">' + label + ' <svg width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 1l4 4 4-4"/></svg></button>';
  document.getElementById("machine-filter-btn").addEventListener("click", mostrarModalSeleccionMaquinas);
}

export function selectMaquina(maquina) {
  state.selectedMaquina = maquina;
  setCookie(MAQ_COOKIE, maquina);
  renderMachineFilter();
  renderComandos();
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

  if (state.selectedMaquina && state.selectedMaquina !== "all") {
    filtered = filtered.filter(function (c) {
      return extractMaquina(c.ruta) === state.selectedMaquina;
    });
  }

  if (state.selectedFolderId !== "all") {
    filtered = pool.filter(function (c) {
      const ids = state.commandFolders[c.com_id] || [];
      return ids.includes(state.selectedFolderId);
    });
  }

  let folderName = "";
  if (state.selectedFolderId !== "all") {
    const found = state.folders.find(function (f) { return f.CAR_ID === state.selectedFolderId; });
    if (found) folderName = found.CAR_NOMBRE;
  }

  if (folderName) {
    folderBadge.textContent = folderName;
    folderBadge.style.display = "inline";
  } else {
    folderBadge.style.display = "none";
  }

  const isFolderView = state.selectedFolderId !== "all";
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
    state.maquinasDisponibles = detectarMaquinas(state.comandosCache);
    if (!state.selectedMaquina || !state.maquinasDisponibles.includes(state.selectedMaquina)) {
      state.selectedMaquina = getCookie(MAQ_COOKIE) || "all";
      if (state.selectedMaquina !== "all" && !state.maquinasDisponibles.includes(state.selectedMaquina)) {
        state.selectedMaquina = "all";
      }
    }
    renderMachineFilter();
    searchInput.value = "";
    renderComandos();
    mostrarSiNoHayMaquinas();
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

  const machineBtn = document.getElementById("machine-select-btn");
  if (machineBtn) {
    machineBtn.addEventListener("click", function () {
      mostrarModalMaquinas();
    });
  }

  if (getToken()) cargarComandos();
}

function mostrarModalSeleccionMaquinas() {
  const maquinas = state.maquinasDisponibles || [];
  let html = '<div class="machine-list">';
  html += '<div class="machine-option' + (state.selectedMaquina === "all" ? " active" : "") + '" data-maquina="all"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> Todas las maquinas</div>';
  maquinas.forEach(function (m) {
    html += '<div class="machine-option' + (state.selectedMaquina === m ? " active" : "") + '" data-maquina="' + escapeHtml(m) + '"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" y1="20" x2="22" y2="20"/></svg> ' + escapeHtml(m) + '</div>';
  });
  html += '</div>';

  document.getElementById("modal-cancel").style.display = "inline-block";
  document.getElementById("modal-cancel").textContent = "Cerrar";
  document.getElementById("modal-cancel").onclick = hideModal;
  document.getElementById("modal-save").style.display = "none";
  showModal("Filtrar por maquina", html);

  document.querySelectorAll(".machine-option").forEach(function (el) {
    el.addEventListener("click", function () {
      selectMaquina(el.dataset.maquina);
      hideModal();
    });
  });
}

function mostrarModalMaquinas() {
  const token = getToken() || localStorage.getItem("access_token_backup") || "";
  let osActual = "linux";

  function generarHTML(os) {
    const esLinux = os === "linux";
    const scriptName = esLinux ? "upload_history.sh" : "upload_history.ps1";
    const btnLabel = "Descargar " + scriptName;
    const tabClass = function (tab) { return "os-tab" + (tab === os ? " active" : ""); };

    let paso2html;
    if (esLinux) {
      paso2html =
        '<div class="paso-texto">' +
          '<strong>Ejecutalo en tu terminal</strong>' +
          '<p>Abre una terminal y navega a la carpeta donde se descargo el archivo (normalmente <strong>Descargas</strong>). Luego corre:</p>' +
          '<code class="paso-code">cd ~/Downloads && bash upload_history.sh</code>' +
          '<p class="paso-nota">Si lo guardaste en otra carpeta, usa <code>cd /ruta/donde/lo/guardaste</code></p>' +
        '</div>';
    } else {
      paso2html =
        '<div class="paso-texto">' +
          '<strong>Ejecutalo en PowerShell</strong>' +
          '<p>Abre <strong>PowerShell</strong> como usuario normal y navega a la carpeta donde se descargo el archivo (normalmente <strong>Descargas</strong>). Luego corre:</p>' +
          '<code class="paso-code">cd ~\\Downloads && .\\upload_history.ps1</code>' +
          '<p class="paso-nota">Si es la primera vez, ejecuta antes: <code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code></p>' +
        '</div>';
    }

    return (
      '<div class="os-selector">' +
        '<button class="' + tabClass("linux") + '" data-os="linux">Linux / Mac</button>' +
        '<button class="' + tabClass("windows") + '" data-os="windows">Windows</button>' +
      '</div>' +
      '<div class="pasos-guide">' +
        '<div class="paso">' +
          '<span class="paso-num">1</span>' +
          '<div class="paso-texto">' +
            '<strong>Descarga el script</strong>' +
            '<p>Haz clic en el boton de abajo para descargar el archivo <code>' + scriptName + '</code> con tu token incluido.</p>' +
          '</div>' +
        '</div>' +
        '<div class="paso">' +
          '<span class="paso-num">2</span>' +
          paso2html +
        '</div>' +
        '<div class="paso">' +
          '<span class="paso-num">3</span>' +
          '<div class="paso-texto">' +
            '<strong>Actualiza la pagina</strong>' +
            '<p>Presiona <kbd>Ctrl+Shift+R</kbd> o haz clic en "Actualizar" y tus comandos apareceran con el nombre de tu maquina.</p>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<button id="download-script-btn" class="btn-sm" style="width:100%;margin-top:0.75rem;">' + btnLabel + '</button>'
    );
  }

  function render(os) {
    osActual = os;
    document.getElementById("modal-body").innerHTML = generarHTML(os);
    document.getElementById("download-script-btn").addEventListener("click", function () {
      descargarScript(token, osActual);
    });
    document.querySelectorAll(".os-tab").forEach(function (btn) {
      btn.addEventListener("click", function () {
        render(this.dataset.os);
      });
    });
  }

  document.getElementById("modal-cancel").style.display = "none";
  document.getElementById("modal-save").textContent = "Cerrar";
  document.getElementById("modal-save").onclick = hideModal;
  showModal("Bajar comandos de este equipo", generarHTML("linux"));
  document.getElementById("download-script-btn").addEventListener("click", function () {
    descargarScript(token, "linux");
  });
  document.querySelectorAll(".os-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      render(this.dataset.os);
    });
  });
}

function descargarScript(token, os) {
  const API_URL = "http://52.87.195.200:8000";
  let contenido, nombreArchivo, tipoMime;

  if (os === "windows") {
    nombreArchivo = "upload_history.ps1";
    tipoMime = "text/x-powershell";
    contenido =
'$API_URL = "' + API_URL + '"\n' +
"$TOKEN = '" + token + "'\n" +
'$HOSTNAME = $env:COMPUTERNAME\n' +
'\n' +
'$histFile = "$env:USERPROFILE\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"\n' +
'if (-not (Test-Path $histFile)) {\n' +
'  Write-Host "No se encontro el historial de PowerShell"\n' +
'  exit 1\n' +
'}\n' +
'\n' +
'$comandos = @()\n' +
'Get-Content $histFile | ForEach-Object {\n' +
'  $line = $_.Trim()\n' +
'  if ($line -and -not $line.StartsWith("#")) {\n' +
'    $comandos += @{ comando = $line; ruta = "[MAQUINA:$HOSTNAME]"; fecha = $null }\n' +
'  }\n' +
'}\n' +
'\n' +
'$body = @{ comandos = $comandos } | ConvertTo-Json -Compress\n' +
"$headers = @{ Authorization = 'Bearer $TOKEN'; 'Content-Type' = 'application/json' }\n" +
'\n' +
'Write-Host "Subiendo $($comandos.Length) comandos..."\n' +
'try {\n' +
'  Invoke-RestMethod -Uri "$API_URL/comandos/importar" -Method Post -Headers $headers -Body $body\n' +
'  Write-Host "Comandos subidos correctamente desde $HOSTNAME"\n' +
'} catch {\n' +
'  Write-Host "Error: $_"\n' +
'}\n';
  } else {
    nombreArchivo = "upload_history.sh";
    tipoMime = "text/x-shellscript";
    contenido =
'#!/bin/bash\n' +
'API_URL="' + API_URL + '"\n' +
'TOKEN="' + token + '"\n' +
'\n' +
'HOSTNAME=$(hostname)\n' +
'HISTFILE="${BASH_HISTFILE:-$HOME/.bash_history}"\n' +
'[ ! -f "$HISTFILE" ] && HISTFILE="$HOME/.zsh_history"\n' +
'[ ! -f "$HISTFILE" ] && { echo "No se encontro .bash_history ni .zsh_history"; exit 1; }\n' +
'\n' +
'python3 -c "\n' +
'import json, sys\n' +
'hist = []\n' +
'with open(\'$HISTFILE\', \'r\', errors=\'ignore\') as f:\n' +
'    for line in f:\n' +
'        line = line.strip().rstrip(\'\\n\')\n' +
'        if not line or line.startswith(\'#\'):\n' +
'            continue\n' +
'        hist.append({\n' +
'            \'comando\': line,\n' +
'            \'ruta\': \'[MAQUINA:${HOSTNAME}]\',\n' +
'            \'fecha\': None\n' +
'        })\n' +
'print(json.dumps({\'comandos\': hist}))\n' +
'" | curl -s -X POST "$API_URL/comandos/importar" \\\n' +
'    -H "Content-Type: application/json" \\\n' +
'    -H "Authorization: Bearer $TOKEN" \\\n' +
'    --data-binary @-\n' +
'\n' +
'echo ""\n';
  }

  const blob = new Blob([contenido], { type: tipoMime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombreArchivo;
  a.click();
  URL.revokeObjectURL(url);
}

export function mostrarSiNoHayMaquinas() {
  const maquinas = state.maquinasDisponibles || [];
  if (maquinas.length === 0) {
    const token = getToken() || localStorage.getItem("access_token_backup") || "";
    if (token) mostrarModalMaquinas();
  }
}
