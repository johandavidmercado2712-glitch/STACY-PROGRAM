<script setup>
import { ref } from 'vue'
import { useCommandStore } from '../stores/commands.js'
import { useFolderStore } from '../stores/folders.js'
import { useModalStore } from '../stores/modal.js'
import { extractMaquina, limpiarRuta, formatearHora, escapeHtml } from '../helpers/utils.js'
import { updateCommandDescription } from '../api.js'

const props = defineProps({ item: Object, folderView: Boolean })
const commands = useCommandStore()
const folders = useFolderStore()
const modal = useModalStore()
const copiedId = ref(null)

function copiarComando(comando) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(comando).then(() => {
      copiedId.value = props.item.com_id
      setTimeout(() => { copiedId.value = null }, 1500)
    }).catch(fallbackCopy)
  } else {
    fallbackCopy()
  }
  function fallbackCopy() {
    const ta = document.createElement('textarea')
    ta.value = comando
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copiedId.value = props.item.com_id
    setTimeout(() => { copiedId.value = null }, 1500)
  }
}

function mostrarDetalles() {
  const maq = extractMaquina(props.item.ruta)
  const rutaLimpia = limpiarRuta(props.item.ruta)
  const comId = props.item.com_id
  const descKey = folders.selectedFolderId + '_' + comId

  modal.open('Detalles del comando', `
    <div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Comando</span>
      <code class="font-mono text-sm text-accent bg-accent-dim px-2.5 py-1.5 rounded-lg inline-block break-all">${escapeHtml(props.item.comando || '')}</code>
    </div>
    <div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Maquina</span>
      <span class="text-sm text-accent font-semibold">${escapeHtml(maq || 'Servidor')}</span>
    </div>
    <div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Hora</span>
      <span class="text-sm text-text">${formatearHora(props.item.fecha)}</span>
    </div>
    <div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Ruta</span>
      <span class="text-sm text-text break-all font-mono">${escapeHtml(rutaLimpia)}</span>
    </div>
    ${maq && rutaLimpia !== props.item.ruta ? `<div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Ruta completa</span>
      <span class="text-xs text-text-secondary break-all font-mono opacity-70">${escapeHtml(props.item.ruta)}</span>
    </div>` : ''}
    <div class="mb-3">
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Carpetas</span>
      <span class="text-sm text-text">${escapeHtml(folders.commandFolders[comId]?.map(id => folders.folders.find(f => f.CAR_ID === id)?.CAR_NOMBRE || '').filter(Boolean).join(', ') || 'Ninguna')}</span>
    </div>
    ${props.folderView ? `<div>
      <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Nota</span>
      <input id="detail-desc-input" type="text" placeholder="Agregar descripcion..." value="${escapeHtml(folders.commandDescriptions[descKey] || '')}" class="w-full px-2.5 py-2 text-sm bg-bg border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] box-border" />
    </div>` : ''}
  `, [
    ...(props.folderView ? [{
      text: 'Cerrar', class: 'btn-sm btn-outline', action: async () => {
        const desc = document.getElementById('detail-desc-input')?.value
        if (desc !== undefined) {
          try { await updateCommandDescription(folders.selectedFolderId, comId, desc) } catch {}
        }
        modal.close()
      }
    }] : [{ text: 'Cerrar', class: 'btn-sm btn-outline', action: () => modal.close() }])
  ])
}

async function mostrarAsignarCarpetas() {
  const comId = props.item.com_id
  const asignadas = folders.commandFolders[comId] || []
  let html = '<div class="flex flex-col">'
  folders.folders.forEach(f => {
    const checked = asignadas.includes(f.CAR_ID) ? 'checked' : ''
    html += `<label class="flex items-center gap-2 px-1.5 py-2 cursor-pointer border-b border-border last:border-b-0 hover:bg-surface-hover rounded-lg -mx-1.5">
      <input type="checkbox" class="folder-cb accent-accent w-4 h-4 cursor-pointer flex-shrink-0" value="${f.CAR_ID}" ${checked} />
      <span class="text-sm text-text font-medium">${escapeHtml(f.CAR_NOMBRE)}</span>
    </label>`
  })
  html += '</div>'
  modal.open('Asignar a carpetas', html, [
    { text: 'Cancelar', class: 'btn-sm btn-outline', action: () => modal.close() },
    { text: 'Guardar', class: 'btn-sm', action: async () => {
      const checks = document.querySelectorAll('.folder-cb:checked')
      const ids = Array.from(checks).map(c => Number(c.value))
      await folders.setCommandFolders(comId, ids)
      modal.close()
    }},
  ])
}

async function quitarDeCarpeta(e) {
  e.stopPropagation()
  if (!confirm('Quitar este comando de la carpeta?')) return
  const carId = folders.selectedFolderId
  if (carId && carId !== 'all') {
    await folders.setCommandFolders(props.item.com_id, (folders.commandFolders[props.item.com_id] || []).filter(id => id !== carId))
  }
}

function onCardClick() {
  mostrarDetalles()
}
</script>

<template>
  <div @click="onCardClick" class="group relative flex flex-col gap-2 px-4 py-3 bg-surface border border-border rounded-xl transition-all hover:border-accent/30 hover:shadow-md hover:-translate-y-0.5 stagger-enter-active cursor-pointer">
    <div class="flex items-center gap-2 min-w-0">
      <span class="text-[0.6rem] font-semibold text-text-secondary bg-bg border border-border rounded-md px-1.5 py-0.5 flex items-center gap-1 flex-shrink-0">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/code.json" class="current-color" trigger="hover" style="width:10px;height:10px"></lord-icon>
        {{ extractMaquina(item.ruta) || 'Servidor' }}
      </span>
      <span class="text-[0.65rem] text-text-secondary/60 tabular-nums whitespace-nowrap">{{ formatearHora(item.fecha) }}</span>
    </div>
    <div class="flex items-start gap-2 min-w-0">
      <code class="font-mono text-sm bg-accent-dim/50 rounded-lg px-3 py-2 text-accent flex-1 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap border border-accent/10 leading-relaxed">{{ item.comando || '(sin comando)' }}</code>
      <button @click.stop="copiarComando(item.comando)" class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-bg border border-border rounded-lg cursor-pointer transition-all hover:bg-accent-dim hover:border-accent/40 active:scale-90 mt-0.5" :title="copiedId === item.com_id ? 'Copiado!' : 'Copiar comando'" type="button">
        <lord-icon v-if="copiedId === item.com_id" src="https://cdn.lordicon.com/rmkpgtpt.json" trigger="hover" colors="primary:#f59e0b" style="width:15px;height:15px"></lord-icon>
        <lord-icon v-else src="https://media.lordicon.com/assets/icons/editor/copy.json" class="current-color text-text-secondary" trigger="hover" style="width:15px;height:15px"></lord-icon>
      </button>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-[0.65rem] text-text-secondary/50 flex items-center gap-1 overflow-hidden text-ellipsis whitespace-nowrap flex-1 min-w-0">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/code.json" class="current-color flex-shrink-0" trigger="hover" style="width:10px;height:10px"></lord-icon>
        {{ limpiarRuta(item.ruta) || '(sin ruta)' }}
      </span>
      <div v-if="folderView" class="flex gap-1 flex-shrink-0">
        <button @click.stop="mostrarDetalles" class="btn-folder-action text-xs" type="button">Detalles</button>
        <button @click.stop="quitarDeCarpeta" class="btn-folder-action btn-folder-action--danger text-xs" type="button">Quitar</button>
      </div>
      <button v-else @click.stop="mostrarAsignarCarpetas" class="text-[0.6rem] font-semibold text-accent bg-accent-dim rounded-full px-2 py-0.5 cursor-pointer whitespace-nowrap overflow-hidden text-ellipsis max-w-[130px] inline-block text-center transition-all hover:bg-accent-dim/80 border border-accent/20 flex-shrink-0 flex items-center gap-1" type="button">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/code.json" colors="primary:#f59e0b" trigger="hover" style="width:10px;height:10px"></lord-icon>
        {{ (folders.commandFolders[item.com_id] || []).length ? (folders.commandFolders[item.com_id] || []).map(id => folders.folders.find(f => f.CAR_ID === id)?.CAR_NOMBRE).filter(Boolean).join(', ') : 'Sin carpeta' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.btn-folder-action {
  font-family: inherit;
  font-weight: 500;
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.2rem 0.45rem;
  cursor: pointer;
  white-space: nowrap;
  transition: all 180ms ease;
}
.btn-folder-action:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-text-secondary);
}
.btn-folder-action--danger {
  color: var(--color-danger);
  border-color: rgba(248,81,73,0.3);
}
.btn-folder-action--danger:hover {
  background: rgba(248,81,73,0.1);
  border-color: var(--color-danger);
}
</style>
