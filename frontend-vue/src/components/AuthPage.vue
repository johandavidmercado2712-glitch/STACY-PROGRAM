<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useCommandStore } from '../stores/commands.js'
import { useNoteStore } from '../stores/notes.js'
import { useFolderStore } from '../stores/folders.js'

const auth = useAuthStore()
const commands = useCommandStore()
const notes = useNoteStore()
const folders = useFolderStore()

const isLogin = ref(true)
const loginUser = ref('')
const loginPass = ref('')
const regUser = ref('')
const regApellidos = ref('')
const regCorreo = ref('')
const regPass = ref('')
const message = ref('')
const messageType = ref('')

async function handleLogin() {
  message.value = ''
  try {
    await auth.login(loginUser.value, loginPass.value)
    commands.cargar()
    notes.cargar()
  } catch (e) {
    message.value = e.message
    messageType.value = 'error'
  }
}

async function handleRegister() {
  message.value = ''
  try {
    const data = await auth.register(regUser.value, regApellidos.value, regCorreo.value, regPass.value)
    message.value = data.mensaje + ' - ahora inicia sesion'
    messageType.value = 'success'
    isLogin.value = true
  } catch (e) {
    message.value = e.message
    messageType.value = 'error'
  }
}
</script>

<template>
  <div class="flex justify-center items-center min-h-screen relative overflow-hidden">
    <div class="absolute inset-0 pointer-events-none" style="background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(245,158,11,0.08) 0%, transparent 60%), radial-gradient(ellipse 60% 50% at 80% 90%, rgba(245,158,11,0.05) 0%, transparent 50%), radial-gradient(ellipse 50% 40% at 20% 80%, rgba(245,158,11,0.04) 0%, transparent 50%)"></div>
    <div class="bg-surface border border-border rounded-2xl w-full max-w-sm shadow-[0_16px_48px_rgba(0,0,0,0.35),0_4px_12px_rgba(0,0,0,0.15)] overflow-hidden relative z-1">
      <div class="bg-gradient-to-br from-accent-dim/30 to-transparent px-8 py-8 pb-6 text-center border-b border-border">
        <div class="inline-flex items-center justify-center w-13 h-13 rounded-xl bg-accent text-[#0d1117] mb-3 shadow-[0_4px_12px_rgba(245,158,11,0.3)]">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </div>
        <h1 class="m-0 text-2xl font-extrabold tracking-tight text-text">STACY</h1>
        <p class="mt-1 text-sm text-text-secondary font-medium">Historial de Comandos</p>
      </div>
      <div class="px-7 pb-7 pt-5">
        <div class="flex gap-2 mb-5 p-1 bg-bg rounded-xl">
          <button @click="isLogin = true" :class="['flex-1 py-2 px-4 text-sm rounded-lg font-semibold cursor-pointer transition-all font-sans border-none', isLogin ? 'bg-surface text-text shadow-[0_1px_3px_rgba(0,0,0,0.3)]' : 'bg-transparent text-text-secondary']" type="button">Iniciar sesion</button>
          <button @click="isLogin = false" :class="['flex-1 py-2 px-4 text-sm rounded-lg font-semibold cursor-pointer transition-all font-sans border-none', !isLogin ? 'bg-surface text-text shadow-[0_1px_3px_rgba(0,0,0,0.3)]' : 'bg-transparent text-text-secondary']" type="button">Registrarse</button>
        </div>

        <form v-if="isLogin" @submit.prevent="handleLogin" class="flex flex-col gap-3">
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <input v-model="loginUser" type="text" placeholder="Usuario" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input v-model="loginPass" type="password" placeholder="Contrasena" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <button type="submit" class="py-2.5 text-sm font-bold border-none bg-accent text-[#0d1117] rounded-lg cursor-pointer transition-all hover:bg-accent-hover hover:shadow-[0_4px_16px_rgba(245,158,11,0.35)] active:scale-97 font-sans">Ingresar</button>
        </form>

        <form v-else @submit.prevent="handleRegister" class="flex flex-col gap-3">
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <input v-model="regUser" type="text" placeholder="Usuario" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <input v-model="regApellidos" type="text" placeholder="Apellidos" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <input v-model="regCorreo" type="email" placeholder="Correo" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <div class="relative flex items-center">
            <svg class="absolute left-3 text-text-secondary opacity-60 pointer-events-none" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input v-model="regPass" type="password" placeholder="Contrasena" required class="w-full py-2.5 pl-10 pr-3 bg-bg border border-border rounded-lg text-sm text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_3px_var(--color-accent-dim)] placeholder:text-text-secondary/70" />
          </div>
          <button type="submit" class="py-2.5 text-sm font-bold border-none bg-accent text-[#0d1117] rounded-lg cursor-pointer transition-all hover:bg-accent-hover hover:shadow-[0_4px_16px_rgba(245,158,11,0.35)] active:scale-97 font-sans">Registrarse</button>
        </form>

        <div class="flex items-center gap-3 my-4 text-text-secondary text-xs">
          <span class="flex-1 h-px bg-border"></span>
          <span>o continua con</span>
          <span class="flex-1 h-px bg-border"></span>
        </div>

        <button @click="window.location.href = 'http://52.87.195.200:8000/auth/google/login'" class="w-full flex items-center justify-center gap-2 py-2.5 text-sm font-semibold bg-bg text-text border border-border rounded-lg cursor-pointer transition-all hover:bg-surface-hover hover:border-text-secondary active:scale-98 font-sans" type="button">
          <svg viewBox="0 0 24 24" width="18" height="18"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          <span>Continuar con Google</span>
        </button>

        <div v-if="message" :class="['mt-3 text-xs text-center font-medium', messageType === 'error' ? 'text-danger' : 'text-success']">{{ message }}</div>
      </div>
    </div>
  </div>
</template>
