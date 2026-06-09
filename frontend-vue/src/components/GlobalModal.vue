<script setup>
import { useModalStore } from '../stores/modal.js'

const modal = useModalStore()

function onOverlayClick(e) {
  if (e.target === e.currentTarget) modal.close()
}
</script>

<template>
  <Teleport to="#modal-root">
    <div v-if="modal.visible" class="fixed inset-0 bg-black/60 flex items-center justify-center z-1000 backdrop-blur-sm animate-[modalFadeIn_180ms_ease]" @click="onOverlayClick">
      <div class="bg-surface border border-border rounded-2xl w-[90%] max-w-[480px] max-h-[80vh] overflow-y-auto shadow-2xl animate-[modalSlideIn_200ms_ease]">
        <div class="flex justify-between items-center px-5 py-4 border-b border-border bg-surface-hover rounded-t-2xl">
          <h3 class="m-0 text-base font-bold text-text">{{ modal.title }}</h3>
          <button @click="modal.close" class="bg-transparent border-none text-text-secondary text-xl cursor-pointer p-0 leading-none w-7 h-7 flex items-center justify-center rounded-lg hover:text-text hover:bg-white/6 transition-all" type="button">&times;</button>
        </div>
        <div class="p-5" v-html="modal.bodyHTML"></div>
        <div v-if="modal.footerActions.length" class="flex justify-end gap-2 px-5 py-3 border-t border-border">
          <button v-for="(btn, i) in modal.footerActions" :key="i" @click="btn.action" :class="['font-sans font-semibold text-xs px-3 py-1.5 rounded-lg cursor-pointer transition-all active:scale-96', btn.class || 'bg-accent text-[#0d1117] hover:bg-accent-hover']" type="button">{{ btn.text }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
