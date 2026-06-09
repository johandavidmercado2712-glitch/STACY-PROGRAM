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
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        STACY
      </span>
    </div>
    <div class="flex items-center gap-2">
      <button @click="theme.toggle" class="w-8 h-8 flex items-center justify-center bg-transparent text-text-secondary border border-border rounded-lg cursor-pointer hover:bg-surface-hover hover:border-text-secondary hover:text-text transition-all active:scale-92" type="button" title="Cambiar tema">
        <svg v-if="theme.isDark" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
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
