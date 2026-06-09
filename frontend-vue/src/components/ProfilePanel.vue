<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { fetchUserProfile } from '../api.js'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])
const auth = useAuthStore()
const profile = ref(null)
const profileLoaded = ref(false)

watch(() => props.open, async (val) => {
  if (val && !profileLoaded.value) {
    try {
      const res = await fetchUserProfile()
      profile.value = res
      profileLoaded.value = true
    } catch { profile.value = null }
  }
})

function cerrarSesion() {
  auth.logout()
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-900 bg-transparent" @click="emit('close')"></div>
    <div :class="['fixed top-[calc(56px_+_0.5rem)] right-6 z-950 w-80 bg-surface border border-border rounded-2xl shadow-2xl overflow-hidden transition-all duration-180', open ? 'opacity-100 translate-y-0 scale-100 pointer-events-auto' : 'opacity-0 -translate-y-1.5 scale-97 pointer-events-none']">
      <div class="flex items-center gap-3 p-5 bg-gradient-to-br from-accent-dim to-transparent border-b border-border">
        <span class="w-11 h-11 rounded-full bg-accent text-[#0d1117] text-lg font-extrabold flex items-center justify-center flex-shrink-0 shadow-[0_2px_8px_rgba(245,158,11,0.3)]">
          {{ auth.user ? auth.user.charAt(0).toUpperCase() : '?' }}
        </span>
        <div class="min-w-0">
          <div class="font-bold text-text truncate">{{ auth.user }}</div>
          <div class="text-xs text-text-secondary font-medium">Perfil de usuario</div>
        </div>
      </div>
      <div class="p-5 space-y-2">
        <div v-if="profile">
          <div class="mb-2">
            <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Usuario</span>
            <span class="text-sm text-text font-medium">{{ profile.username }}</span>
          </div>
          <div class="mb-2">
            <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Apellidos</span>
            <span class="text-sm text-text font-medium">{{ profile.apellidos }}</span>
          </div>
          <div class="mb-2">
            <span class="block text-[0.7rem] text-text-secondary font-semibold uppercase tracking-wide mb-1">Correo</span>
            <span class="text-sm text-text font-medium">{{ profile.correo }}</span>
          </div>
          <hr class="border-border my-3" />
        </div>
        <div v-else class="text-xs text-text-secondary">Cargando...</div>
        <button @click="cerrarSesion" class="w-full flex items-center gap-2 px-3 py-2.5 bg-transparent border border-border rounded-lg text-danger text-sm font-semibold cursor-pointer hover:bg-danger/10 hover:border-danger transition-all" type="button">
          <lord-icon src="https://cdn.lordicon.com/rmkpgtpt.json" class="current-color" trigger="hover" colors="primary:#f85149" style="width:16px;height:16px"></lord-icon>
          Cerrar sesion
        </button>
      </div>
    </div>
  </Teleport>
</template>
