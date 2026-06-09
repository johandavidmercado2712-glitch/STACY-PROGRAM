<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useThemeStore } from '../stores/theme.js'
import { useCommandStore } from '../stores/commands.js'
import ProfilePanel from './ProfilePanel.vue'

const auth = useAuthStore()
const theme = useThemeStore()
const commands = useCommandStore()
const panelOpen = ref(false)

function togglePanel() { panelOpen.value = !panelOpen.value }
function closePanel() { panelOpen.value = false }

function onKeydown(e) { if (e.key === 'Escape') closePanel() }

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <nav class="sticky top-0 z-100 h-14 bg-surface border-b border-border px-6 flex items-center justify-between backdrop-blur-md" v-show="auth.isAuthenticated">
    <div class="flex items-center gap-2">
      <span class="text-accent font-extrabold text-lg tracking-tight flex items-center gap-1.5">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/code.json" trigger="hover" stroke="bold" colors="primary:#f59e0b" style="width:20px;height:20px"></lord-icon>
        STACY
      </span>
    </div>
    <div class="flex items-center gap-2">
      <button @click="theme.toggle" class="w-8 h-8 flex items-center justify-center bg-transparent text-text-secondary border border-border rounded-lg cursor-pointer hover:bg-surface-hover hover:border-text-secondary hover:text-text transition-all active:scale-92" type="button" title="Cambiar tema">
        <lord-icon v-if="theme.isDark" src="https://media.lordicon.com/assets/icons/editor/star.json" class="current-color" trigger="hover" style="width:16px;height:16px"></lord-icon>
        <lord-icon v-else src="https://media.lordicon.com/assets/icons/editor/update.json" class="current-color" trigger="hover" style="width:16px;height:16px"></lord-icon>
      </button>
      <div class="relative">
        <div @click="togglePanel" class="flex items-center gap-1.5 cursor-pointer px-2.5 py-1 rounded-xl border border-transparent hover:bg-surface-hover hover:border-border transition-all">
          <span class="text-xs text-text-secondary font-semibold flex items-center gap-1">
            <span class="w-1.5 h-1.5 bg-success rounded-full inline-block flex-shrink-0"></span>
            {{ auth.user }}
          </span>
          <span class="w-7 h-7 rounded-full bg-accent text-[#0d1117] text-xs font-extrabold flex items-center justify-center flex-shrink-0">
            {{ auth.user ? auth.user.charAt(0).toUpperCase() : '?' }}
          </span>
        </div>
        <ProfilePanel :open="panelOpen" @close="closePanel" />
      </div>
    </div>
  </nav>
</template>
