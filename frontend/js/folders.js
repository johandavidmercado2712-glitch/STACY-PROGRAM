import { state } from './state.js';
import { fetchFolders, createFolder, deleteFolderApi, assignCommandApi, unassignCommandApi, fetchAssignments } from './api.js';

let _onSelectFolder = null;

export function onSelectFolder(callback) {
  _onSelectFolder = callback;
}

export async function loadFolders() {
  try {
    const foldersRes = await fetchFolders();
    state.folders = foldersRes.carpetas || [];
  } catch (e) {
    state.folders = [];
  }

  try {
    const assignRes = await fetchAssignments();
    state.commandFolders = {};
    state.commandDescriptions = {};
    (assignRes.asignaciones || []).forEach(function (a) {
      if (!state.commandFolders[a.COM_ID]) {
        state.commandFolders[a.COM_ID] = [];
      }
      state.commandFolders[a.COM_ID].push(a.CAR_ID);
      state.commandDescriptions[a.CAR_ID + "_" + a.COM_ID] = a.CC_DESCRIPCION || "";
    });
  } catch (e) {
    state.commandFolders = {};
  }
}

export function renderFolders() {
  const folderList = document.getElementById("folder-list");
  const items = folderList.querySelectorAll(".folder-item");
  for (let i = items.length - 1; i >= 2; i--) items[i].remove();

  state.folders.forEach(function (f) {
    const li = document.createElement("li");
    li.className = "folder-item" + (state.selectedFolderId === f.CAR_ID ? " active" : "");
    li.dataset.folderId = f.CAR_ID;

    const info = document.createElement("div");
    info.className = "folder-info";

    const name = document.createElement("span");
    name.className = "folder-name";
    name.textContent = f.CAR_NOMBRE;
    info.appendChild(name);

    if (f.CAR_DESCRIPCION) {
      const desc = document.createElement("span");
      desc.className = "folder-desc";
      desc.textContent = f.CAR_DESCRIPCION;
      info.appendChild(desc);
    }

    const count = document.createElement("span");
    count.className = "folder-count";
    count.textContent = Object.values(state.commandFolders).filter(function (ids) {
      return Array.isArray(ids) && ids.includes(f.CAR_ID);
    }).length;

    const del = document.createElement("button");
    del.className = "folder-delete";
    del.textContent = "\u00d7";
    del.title = "Eliminar carpeta";
    del.addEventListener("click", function (e) {
      e.stopPropagation();
      deleteFolder(f.CAR_ID);
    });

    li.appendChild(info);
    li.appendChild(count);
    li.appendChild(del);
    li.addEventListener("click", function () { selectFolder(f.CAR_ID); });

    folderList.appendChild(li);
  });

  const allItems = folderList.querySelectorAll(".folder-item");
  allItems.forEach(function (el) {
    const fid = el.dataset.folderId;
    el.classList.toggle("active",
      (fid === "all" && state.selectedFolderId === "all") ||
      (fid === "uncategorized" && state.selectedFolderId === "uncategorized") ||
      (fid !== "all" && fid !== "uncategorized" && fid == state.selectedFolderId)
    );
  });

  document.getElementById("count-all").textContent = state.comandosCache.length;
  const uncatCount = state.comandosCache.filter(function (c) {
    const ids = state.commandFolders[c.com_id];
    return !ids || ids.length === 0;
  }).length;
  document.getElementById("count-uncategorized").textContent = uncatCount;
}

export async function addFolder(name, description) {
  try {
    await createFolder(name, description);
    await loadFolders();
    renderFolders();
  } catch (e) {
    // silently fail, could show error message
  }
}

export async function deleteFolder(id) {
  try {
    await deleteFolderApi(id);
    if (state.selectedFolderId === id) state.selectedFolderId = "all";
    await loadFolders();
    renderFolders();
  } catch (e) {
    // silently fail
  }
}

export function selectFolder(id) {
  state.selectedFolderId = id;
  renderFolders();
  if (_onSelectFolder) _onSelectFolder(id);
}

export async function setCommandFolders(comId, newFolderIds) {
  if (!comId) return;
  const currentIds = state.commandFolders[comId] || [];

  const toAdd = newFolderIds.filter(function (id) { return !currentIds.includes(id); });
  const toRemove = currentIds.filter(function (id) { return !newFolderIds.includes(id); });

  try {
    for (const carId of toAdd) {
      await assignCommandApi(carId, comId);
    }
    for (const carId of toRemove) {
      await unassignCommandApi(carId, comId);
    }
    await loadFolders();
    renderFolders();
  } catch (e) {
    // silently fail
  }
}

export function showModal(title, bodyHTML) {
  document.getElementById("modal-title").textContent = title;
  document.getElementById("modal-body").innerHTML = bodyHTML;
  document.getElementById("modal-overlay").style.display = "flex";
}

export function hideModal() {
  document.getElementById("modal-overlay").style.display = "none";
}

export function initFolders() {
  document.querySelector('[data-folder-id="all"]').addEventListener("click", function () {
    selectFolder("all");
  });
  document.querySelector('[data-folder-id="uncategorized"]').addEventListener("click", function () {
    selectFolder("uncategorized");
  });

  document.getElementById("add-folder-btn").addEventListener("click", function () {
    showModal("Nueva carpeta",
      '<input type="text" id="folder-name-input" placeholder="Nombre de la carpeta" class="modal-input" />' +
      '<textarea id="folder-desc-input" placeholder="Descripcion..." rows="2" class="modal-input" style="margin-top:0.5rem;resize:vertical;"></textarea>'
    );

    document.getElementById("modal-save").onclick = async function () {
      const name = document.getElementById("folder-name-input").value.trim();
      if (!name) return;
      await addFolder(name, document.getElementById("folder-desc-input").value.trim());
      hideModal();
    };
    document.getElementById("modal-cancel").onclick = hideModal;
    document.getElementById("modal-close").onclick = hideModal;
    document.getElementById("modal-overlay").onclick = function (e) {
      if (e.target === this) hideModal();
    };

    setTimeout(function () {
      const inp = document.getElementById("folder-name-input");
      if (inp) inp.focus();
    }, 100);
  });
}
