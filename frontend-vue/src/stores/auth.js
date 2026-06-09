import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister } from '../api.js'
import { setCookie, getCookie, deleteCookie } from '../helpers/cookie.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => !!token.value)

  function loadToken() {
    const urlParams = new URLSearchParams(window.location.search)
    const urlToken = urlParams.get("token")
    const urlUser = urlParams.get("user")
    if (urlToken && urlUser) {
      setAuth(urlToken, urlUser)
      window.history.replaceState({}, "", window.location.pathname)
      return
    }
    token.value = getCookie("access_token") || localStorage.getItem("access_token_backup")
    user.value = getCookie("token_user") || localStorage.getItem("token_user_backup")
  }

  function setAuth(newToken, username) {
    token.value = newToken
    user.value = username
    setCookie("access_token", newToken)
    setCookie("token_user", username)
    localStorage.setItem("access_token_backup", newToken)
    localStorage.setItem("token_user_backup", username)
    error.value = ''
  }

  function clearAuth() {
    token.value = null
    user.value = null
    deleteCookie("access_token")
    deleteCookie("token_user")
    localStorage.removeItem("access_token_backup")
    localStorage.removeItem("token_user_backup")
  }

  async function login(username, password) {
    loading.value = true
    error.value = ''
    try {
      const data = await apiLogin(username, password)
      setAuth(data.access_token, username)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(username, apellidos, correo, password) {
    loading.value = true
    error.value = ''
    try {
      return await apiRegister(username, apellidos, correo, password)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function logout() {
    clearAuth()
  }

  return { token, user, loading, error, isAuthenticated, loadToken, setAuth, clearAuth, login, register, logout }
})
