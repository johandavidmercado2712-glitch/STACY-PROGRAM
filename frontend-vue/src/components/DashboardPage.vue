<script setup>
import { onMounted } from 'vue'
import { useCommandStore } from '../stores/commands.js'
import { useFolderStore } from '../stores/folders.js'
import { useNoteStore } from '../stores/notes.js'
import Sidebar from './Sidebar.vue'
import Toolbar from './Toolbar.vue'
import CommandPanel from './CommandPanel.vue'

const commands = useCommandStore()
const folders = useFolderStore()
const notes = useNoteStore()

onMounted(() => {
  commands.cargar().then(() => folders.load())
  notes.cargar()
})
</script>

<template>
  <main class="w-full px-6 pt-4 pb-8">
    <div class="flex gap-4 items-start flex-col md:flex-row">
      <Sidebar />
      <div class="flex-1 min-w-0">
        <Toolbar />
        <CommandPanel />
      </div>
    </div>
  </main>
</template>
