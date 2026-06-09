<script setup>
import { ref, computed } from 'vue'
import { useFolderStore } from '../stores/folders.js'
import { useCommandStore } from '../stores/commands.js'

const folderStore = useFolderStore()
const commandStore = useCommandStore()

const folderCounts = computed(() => {
  const counts = {}
  Object.values(folderStore.commandFolders).forEach(ids => {
    ids.forEach(carId => {
      counts[carId] = (counts[carId] || 0) + 1
    })
  })
  return counts
})
const showForm = ref(false)
const newName = ref('')
const newDesc = ref('')

function select(id) {
  commandStore.selectFolder(id)
  folderStore.select(id)
}

async function addFolder() {
  if (!newName.value.trim()) return
  await folderStore.create(newName.value.trim(), newDesc.value.trim())
  newName.value = ''
  newDesc.value = ''
  showForm.value = false
}

async function removeFolder(carId, e) {
  e.stopPropagation()
  if (!confirm('Eliminar esta carpeta?')) return
  await folderStore.remove(carId)
  commandStore.selectFolder('all')
  folderStore.select('all')
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2 pb-2 border-b border-border">
      <h3 class="text-xs font-bold uppercase tracking-wide text-text-secondary m-0 flex items-center gap-1.5">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        Carpetas
      </h3>
      <button @click="showForm = !showForm" class="bg-transparent border border-border text-text-secondary w-7 h-7 rounded-lg cursor-pointer text-lg leading-none flex items-center justify-center hover:bg-accent-dim hover:border-accent hover:text-accent hover:scale-108 active:scale-95 transition-all" type="button" title="Nueva carpeta">+</button>
    </div>

    <ul class="list-none m-0 p-0 space-y-1">
      <li @click="select('all')" :class="['flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer border transition-all', folderStore.selectedFolderId === 'all' ? 'bg-accent-dim/30 border-accent/30 shadow-sm' : 'bg-transparent border-transparent hover:bg-surface-hover']">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="folderStore.selectedFolderId === 'all' ? 'text-accent' : 'text-text-secondary'"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <div class="flex-1 min-w-0">
          <span class="text-sm font-semibold text-text truncate block">Todos los comandos</span>
        </div>
        <span class="text-[0.65rem] text-text-secondary bg-bg border border-border rounded-md px-1.5 py-0.5 font-semibold min-w-6 text-center">{{ commandStore.comandosCache.length }}</span>
      </li>
      <li v-for="f in folderStore.folders" :key="f.CAR_ID" @click="select(f.CAR_ID)" :class="['flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer border transition-all group', folderStore.selectedFolderId === f.CAR_ID ? 'bg-accent-dim/30 border-accent/30 shadow-sm' : 'bg-transparent border-transparent hover:bg-surface-hover']">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="folderStore.selectedFolderId === f.CAR_ID ? 'text-accent' : 'text-text-secondary'" class="flex-shrink-0"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <div class="flex-1 min-w-0">
          <span class="text-sm font-semibold text-text truncate block">{{ f.CAR_NOMBRE }}</span>
          <span v-if="f.CAR_DESCRIPCION" class="text-[0.65rem] text-text-secondary truncate block mt-0.5">{{ f.CAR_DESCRIPCION }}</span>
        </div>
        <span class="text-[0.65rem] text-text-secondary bg-bg border border-border rounded-md px-1.5 py-0.5 font-semibold min-w-6 text-center flex-shrink-0">{{ folderCounts[f.CAR_ID] || 0 }}</span>
        <button @click="removeFolder(f.CAR_ID, $event)" class="bg-transparent border-none text-text-secondary cursor-pointer p-0.5 rounded flex-shrink-0 opacity-0 group-hover:opacity-50 hover:opacity-100! hover:text-danger hover:bg-danger/10 transition-all flex items-center justify-center w-5 h-5" type="button" title="Eliminar">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </li>
    </ul>

    <div v-if="showForm" class="mt-3 p-3 bg-surface border border-border rounded-xl flex flex-col gap-2.5 shadow-sm">
      <input v-model="newName" type="text" placeholder="Nombre de la carpeta" class="w-full px-3 py-2 text-sm bg-bg border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
      <textarea v-model="newDesc" placeholder="Descripcion..." rows="2" class="w-full px-3 py-2 text-sm bg-bg border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] placeholder:text-text-secondary/70 resize-vertical"></textarea>
      <div class="flex gap-2 pt-0.5">
        <button @click="addFolder" class="flex-1 py-1.5 px-3 text-xs font-semibold border-none bg-accent text-[#0d1117] rounded-lg cursor-pointer transition-all hover:bg-accent-hover active:scale-96 font-sans flex items-center justify-center gap-1">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          Crear
        </button>
        <button @click="showForm = false" class="py-1.5 px-3 text-xs font-semibold bg-transparent text-text-secondary border border-border rounded-lg cursor-pointer transition-all hover:border-text-secondary hover:text-text active:scale-96 font-sans">Cancelar</button>
      </div>
    </div>
  </div>
</template>
