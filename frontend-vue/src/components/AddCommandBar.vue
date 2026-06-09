<script setup>
import { ref, computed } from 'vue'
import { useCommandStore } from '../stores/commands.js'
import { useFolderStore } from '../stores/folders.js'

const commands = useCommandStore()
const folders = useFolderStore()
const search = ref('')
const showResults = ref(false)

const unassigned = computed(() => {
  return commands.comandosCache.filter(c => {
    const ids = folders.commandFolders[c.com_id] || []
    return !ids.includes(folders.selectedFolderId)
  })
})

const results = computed(() => {
  if (!search.value) return []
  const q = search.value.toLowerCase()
  return unassigned.value.filter(c =>
    (c.comando || '').toLowerCase().includes(q) || (c.ruta || '').toLowerCase().includes(q)
  ).slice(0, 10)
})

function cerrarResultados() {
  setTimeout(() => { showResults.value = false }, 200)
}

async function assign(item) {
  await folders.setCommandFolders(item.com_id, [...(folders.commandFolders[item.com_id] || []), folders.selectedFolderId])
  search.value = ''
  showResults.value = false
}
</script>

<template>
  <div class="mb-3 p-2.5 bg-surface border border-border rounded-lg">
    <div class="text-xs text-text-secondary font-semibold mb-1.5">Agregar comando a esta carpeta</div>
    <div class="relative">
      <input v-model="search" @focus="showResults = true" @blur="cerrarResultados" type="text" placeholder="Buscar comando..." class="w-full px-2.5 py-2 text-sm bg-bg text-text border border-border rounded-lg outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] box-border font-sans" />
      <div v-if="showResults && results.length" class="absolute top-full left-0 right-0 mt-1 max-h-55 overflow-y-auto bg-surface border border-border rounded-lg z-10 shadow-lg">
        <div v-for="r in results" :key="r.com_id" @mousedown="assign(r)" class="flex items-center gap-2 px-2 py-1.5 cursor-pointer rounded hover:bg-surface-hover">
          <code class="font-mono text-xs text-accent whitespace-nowrap overflow-hidden text-ellipsis">{{ r.comando }}</code>
          <span class="text-[0.7rem] text-text-secondary italic overflow-hidden text-ellipsis whitespace-nowrap">{{ r.ruta }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
