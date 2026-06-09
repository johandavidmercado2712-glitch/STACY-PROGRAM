<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCommandStore } from '../stores/commands.js'
import { useModalStore } from '../stores/modal.js'
import { formatearHora, limpiarRuta, escapeHtml } from '../helpers/utils.js'

const commands = useCommandStore()
const modal = useModalStore()
const search = ref('')

const filteredBySearch = computed(() => {
  if (!search.value) return commands.filteredComandos
  const q = search.value.toLowerCase()
  return commands.filteredComandos.filter(c =>
    (c.comando || '').toLowerCase().includes(q) || (c.ruta || '').toLowerCase().includes(q)
  )
})

const maquinaHandler = (e) => {
  const opt = e.target.closest('.machine-option')
  if (!opt) return
  const m = opt.dataset.maquina
  if (m !== undefined) {
    commands.selectMaquina(m)
    modal.close()
    document.removeEventListener('click', maquinaHandler)
  }
}

function mostrarFiltroMaquinas() {
  const optClass = 'machine-option flex items-center gap-2 px-3 py-2.5 cursor-pointer rounded-lg text-sm font-medium text-text border border-transparent transition-all duration-180 hover:bg-surface-hover hover:border-border'
  let html = '<div class="flex flex-col gap-0.5">'
  html += '<div class="' + optClass + '" data-maquina="all">Todas las maquinas</div>'
  commands.maquinasDisponibles.forEach(m => {
    html += '<div class="' + optClass + '" data-maquina="' + escapeHtml(m) + '">' + escapeHtml(m) + '</div>'
  })
  html += '</div>'
  modal.open('Filtrar por maquina', html, [
    { text: 'Cerrar', class: 'btn-sm btn-outline', action: () => {
      document.removeEventListener('click', maquinaHandler)
      modal.close()
    }},
  ])
  setTimeout(() => document.addEventListener('click', maquinaHandler), 50)
}

function mostrarGuiaDescarga() {
  const token = document.cookie.match(/(?:^| )access_token=([^;]*)/)?.[1] || localStorage.getItem('access_token_backup')
  const scriptBash = `#!/bin/bash
# --- STACY upload script (Linux/macOS) ---
# Generated: ${new Date().toISOString()}
TOKEN="${token || 'TOKEN_NO_ENCONTRADO'}"
HISTFILE="$HOME/.bash_history"
if [ ! -f "$HISTFILE" ]; then
  echo "No se encontro .bash_history en $HOME"
  exit 1
fi
echo "Subiendo historial a STACY..."
curl -s -X POST "http://52.87.195.200:8000/comandos/importar" \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  --data-binary @"$HISTFILE"
echo ""
echo "Listo."
`
  const scriptPs1 = `# --- STACY upload script (Windows PowerShell) ---
# Generated: ${new Date().toISOString()}
$TOKEN="${token || 'TOKEN_NO_ENCONTRADO'}"
$HISTFILE = "$env:USERPROFILE\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt"
if (!(Test-Path $HISTFILE)) {
  Write-Host "No se encontro el historial de PowerShell en $HISTFILE"
  exit 1
}
Write-Host "Subiendo historial a STACY..."
$body = Get-Content $HISTFILE -Raw
Invoke-RestMethod -Uri "http://52.87.195.200:8000/comandos/importar" -Method Post -Headers @{Authorization = "Bearer $TOKEN"} -ContentType "application/json" -Body $body
Write-Host ""
Write-Host "Listo."
`
  const os = window.__stacy_os || 'linux'
  const tabClass = (tab) => os === tab
    ? 'flex-1 py-1.5 text-xs font-semibold border-none bg-bg text-accent rounded-lg cursor-pointer font-sans shadow-sm'
    : 'flex-1 py-1.5 text-xs font-semibold border-none bg-transparent text-text-secondary cursor-pointer font-sans'
  modal.open('Bajar comandos de este equipo', `
    <div class="flex gap-1 p-0.5 bg-surface border border-border rounded-xl mb-4">
      <button class="${tabClass('linux')}" onclick="window.__stacy_os='linux';window.__stacyRefreshGuide()">Linux / macOS</button>
      <button class="${tabClass('windows')}" onclick="window.__stacy_os='windows';window.__stacyRefreshGuide()">Windows</button>
    </div>
    <div class="flex flex-col gap-4">
      <div class="flex gap-3 p-3 bg-bg border border-border rounded-lg items-start">
        <span class="w-7 h-7 rounded-full bg-accent text-[#0d1117] text-xs font-extrabold flex items-center justify-center flex-shrink-0 mt-px">1</span>
        <div class="flex-1 min-w-0">
          <strong class="text-sm text-text block mb-1">Abre la terminal</strong>
          <p class="text-xs text-text-secondary m-0 leading-relaxed">${os === 'linux' ? 'Abre tu terminal (Linux/macOS).' : 'Abre PowerShell como Administrador en Windows.'}</p>
        </div>
      </div>
      <div class="flex gap-3 p-3 bg-bg border border-border rounded-lg items-start">
        <span class="w-7 h-7 rounded-full bg-accent text-[#0d1117] text-xs font-extrabold flex items-center justify-center flex-shrink-0 mt-px">2</span>
        <div class="flex-1 min-w-0">
          <strong class="text-sm text-text block mb-1">Descarga el script</strong>
          <p class="text-xs text-text-secondary m-0 leading-relaxed">Usa el boton "Descargar script" abajo y guardalo en tu carpeta de <strong>Descargas</strong>.</p>
        </div>
      </div>
      <div class="flex gap-3 p-3 bg-bg border border-border rounded-lg items-start">
        <span class="w-7 h-7 rounded-full bg-accent text-[#0d1117] text-xs font-extrabold flex items-center justify-center flex-shrink-0 mt-px">3</span>
        <div class="flex-1 min-w-0">
          <strong class="text-sm text-text block mb-1">Ejecuta el script</strong>
          <p class="text-xs text-text-secondary m-0 leading-relaxed">En la terminal, navega a Descargas y ejecuta:</p>
          ${os === 'linux'
            ? '<code class="block font-mono text-xs bg-surface border border-border rounded-lg px-3 py-2 text-accent mt-1">cd ~/Downloads && chmod +x upload_history.sh && ./upload_history.sh</code>'
            : '<code class="block font-mono text-xs bg-surface border border-border rounded-lg px-3 py-2 text-accent mt-1">cd $env:USERPROFILE\\Downloads\\ &amp; .\\upload_history.ps1</code>'}
          <p class="text-xs text-text-secondary italic mt-1">Los comandos se subiran al servidor y apareceran en STACY automaticamente.</p>
        </div>
      </div>
    </div>
  `, [
    { text: os === 'linux' ? 'Descargar script (.sh)' : 'Descargar script (.ps1)', class: 'bg-accent text-[#0d1117]', action: () => {
      const a = document.createElement('a')
      a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(os === 'linux' ? scriptBash : scriptPs1)
      a.download = os === 'linux' ? 'upload_history.sh' : 'upload_history.ps1'
      a.click()
    }},
    { text: 'Cerrar', class: 'btn-sm btn-outline', action: () => modal.close() },
  ])
  window.__stacyRefreshGuide = () => mostrarGuiaDescarga()
}
</script>

<template>
  <div class="flex flex-col md:flex-row items-stretch md:items-center gap-3 mb-3">
    <div class="flex-1 min-w-0">
      <input v-model="search" type="text" placeholder="Filtrar comandos..." class="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent placeholder:text-text-secondary/60" />
    </div>
    <div class="flex items-center gap-2 flex-shrink-0 flex-wrap">
      <button @click="mostrarFiltroMaquinas" class="btn-outline text-xs" type="button">Filtrar maquina</button>
      <div class="flex gap-0.5 p-0.5 bg-surface border border-border rounded-xl">
        <button @click="commands.setVista('recent')" :class="['text-xs px-2.5 py-1 rounded-lg border-none font-semibold cursor-pointer transition-all font-sans', commands.vistaActual === 'recent' ? 'bg-bg text-accent shadow-sm' : 'bg-transparent text-text-secondary hover:text-text']" type="button">Ultimos 11</button>
        <button @click="commands.setVista('all')" :class="['text-xs px-2.5 py-1 rounded-lg border-none font-semibold cursor-pointer transition-all font-sans', commands.vistaActual === 'all' ? 'bg-bg text-accent shadow-sm' : 'bg-transparent text-text-secondary hover:text-text']" type="button">Todos</button>
      </div>
      <button @click="commands.cargar" class="btn-outline text-xs flex items-center gap-1" type="button">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/update.json" class="current-color" trigger="hover" style="width:14px;height:14px"></lord-icon>
        Actualizar
      </button>
      <button @click="mostrarGuiaDescarga" class="btn-accent text-xs whitespace-nowrap" type="button">Bajar comandos de este equipo</button>
    </div>
  </div>
</template>

<style scoped>
.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.7rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  transition: all 180ms ease;
  white-space: nowrap;
}
.btn-outline:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-text-secondary);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.btn-outline:active { transform: scale(0.97); }

.btn-accent {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  font-weight: 600;
  border: none;
  background: var(--color-accent);
  color: #0d1117;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  transition: all 180ms ease;
}
.btn-accent:hover {
  background: var(--color-accent-hover);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.25);
}
.btn-accent:active { transform: scale(0.97); }

.btn-sm {
  font-size: 0.78rem;
  padding: 0.4rem 0.75rem;
  font-weight: 600;
  border: none;
  background: var(--color-accent);
  color: #0d1117;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  transition: all 180ms ease;
}
.btn-sm:hover {
  background: var(--color-accent-hover);
  box-shadow: 0 2px 6px rgba(245,158,11,0.25);
}
.btn-sm:active { transform: scale(0.96); }
.btn-sm.btn-outline {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.btn-sm.btn-outline:hover {
  border-color: var(--color-text-secondary);
  color: var(--color-text);
  box-shadow: none;
}
.machine-option {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-radius: 8px;
  color: var(--color-text);
  font-size: 0.88rem;
  font-weight: 500;
  transition: background 180ms ease;
  border: 1px solid transparent;
}
.machine-option:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}
</style>
