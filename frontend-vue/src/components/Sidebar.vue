<script setup>
import FolderSection from './FolderSection.vue'
import NoteSection from './NoteSection.vue'
</script>

<template>
  <aside class="w-full md:w-60 flex-shrink-0 bg-surface border border-border rounded-xl p-3.5 md:sticky md:top-[calc(56px_+_1rem)] md:max-h-[calc(100vh_-_56px_-_2rem)] overflow-y-auto">
    <FolderSection />
    <div class="h-px bg-border my-3"></div>
    <NoteSection />
  </aside>
</template>
