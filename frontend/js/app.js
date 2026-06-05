import { initAuth, actualizarUI, getToken, onLogin } from './auth.js?v=5';
import { initFolders, loadFolders, renderFolders, onSelectFolder } from './folders.js?v=5';
import { initCommands, renderComandos, cargarComandos, onCommandsLoaded } from './commands.js?v=5';
import { initTheme } from './theme.js?v=5';
import { initProfile } from './profile.js?v=5';

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initAuth();
  initProfile();
  initFolders();
  initCommands();

  onLogin(function () {
    cargarComandos();
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
