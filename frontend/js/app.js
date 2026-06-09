import { initAuth, actualizarUI, getToken, onLogin } from './auth.js?v=9';
import { initFolders, loadFolders, renderFolders, onSelectFolder } from './folders.js?v=9';
import { initCommands, renderComandos, cargarComandos, onCommandsLoaded } from './commands.js?v=9';
import { initTheme } from './theme.js?v=9';
import { initProfile } from './profile.js?v=9';
import { initNotas, cargarNotas } from './notas.js?v=9';

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initAuth();
  initProfile();
  initFolders();
  initCommands();
  initNotas();

  onLogin(function () {
    cargarComandos();
    cargarNotas();
  });

  onSelectFolder(function (folderId) {
    const searchBar = document.querySelector(".search-bar");
    if (searchBar) {
      searchBar.style.display = (folderId === "all" || folderId === "uncategorized") ? "" : "none";
    }
    renderComandos();
  });

  onCommandsLoaded(async function () {
    await loadFolders();
    renderFolders();
  });
});
