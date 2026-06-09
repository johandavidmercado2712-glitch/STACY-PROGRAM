<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth.js'
import { useThemeStore } from './stores/theme.js'
import Navbar from './components/Navbar.vue'
import AuthPage from './components/AuthPage.vue'
import DashboardPage from './components/DashboardPage.vue'
import GlobalModal from './components/GlobalModal.vue'

const auth = useAuthStore()
const theme = useThemeStore()

onMounted(() => {
  theme.init()
  auth.loadToken()
})
</script>

<template>
  <Navbar />
  <AuthPage v-if="!auth.isAuthenticated" />
  <DashboardPage v-else />
  <GlobalModal />
</template>
