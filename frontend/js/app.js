import { initAuth, actualizarUI, getToken, onLogin } from './auth.js';
import { initFolders, loadFolders, renderFolders, onSelectFolder } from './folders.js';
import { initCommands, renderComandos, cargarComandos, onCommandsLoaded } from './commands.js';
import { initTheme } from './theme.js';

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initAuth();
  initFolders();
  initCommands();

  onLogin(function () {
    cargarComandos();
  });

  onSelectFolder(function () {
    renderComandos();
  });

  onCommandsLoaded(async function () {
    await loadFolders();
    renderFolders();
  });
});
