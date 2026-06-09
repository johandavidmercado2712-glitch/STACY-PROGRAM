<script setup>
import { computed } from 'vue'
import { useCommandStore } from '../stores/commands.js'
import { useFolderStore } from '../stores/folders.js'
import CommandItem from './CommandItem.vue'
import AddCommandBar from './AddCommandBar.vue'

const commands = useCommandStore()
const folders = useFolderStore()

const folderName = computed(() => {
  if (folders.selectedFolderId === 'all') return ''
  const f = folders.folders.find(f => f.CAR_ID === folders.selectedFolderId)
  return f ? f.CAR_NOMBRE : ''
})

const isFolderView = computed(() => folders.selectedFolderId !== 'all')

const displayList = computed(() => {
  let pool = commands.filteredComandos
  if (isFolderView.value) {
    pool = pool.filter(c => {
      const ids = folders.commandFolders[c.com_id] || []
      return ids.includes(folders.selectedFolderId)
    })
  }
  return pool
})
</script>

<template>
  <section class="bg-surface border border-border rounded-2xl px-4 pt-4 pb-1 shadow-xl">
    <div class="flex justify-between items-center gap-2">
      <h2 class="m-0 text-base font-bold text-text">{{ folderName || 'Todos los comandos' }}</h2>
      <span v-if="folderName" class="text-[0.7rem] text-accent bg-accent-dim border border-accent/25 rounded-full px-2 py-0.5 font-semibold whitespace-nowrap overflow-hidden text-ellipsis max-w-45">{{ folderName }}</span>
    </div>

    <AddCommandBar v-if="isFolderView" />

    <p v-if="commands.loading" class="mt-2 text-sm text-text-secondary">Cargando comandos...</p>
    <p v-else-if="commands.error" class="mt-2 text-sm text-danger">{{ commands.error }}</p>
    <p v-else-if="displayList.length === 0" class="mt-2 text-sm text-text-secondary">{{ folderName ? 'Sin comandos en ' + folderName + '.' : 'Sin comandos disponibles.' }}</p>
    <p v-else class="mt-2 text-sm text-text-secondary">Mostrando {{ displayList.length }} comando{{ displayList.length !== 1 ? 's' : '' }}</p>

    <div v-if="displayList.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2 m-2 mt-1.5">
      <CommandItem v-for="item in displayList" :key="item.com_id" :item="item" :folderView="isFolderView" />
    </div>
  </section>
</template>
