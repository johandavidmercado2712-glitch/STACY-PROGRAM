import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)

  function init() {
    const saved = localStorage.getItem("stacy_theme")
    const prefers = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"
    isDark.value = (saved || prefers) !== "light"
    apply()
  }

  function apply() {
    document.documentElement.setAttribute("data-theme", isDark.value ? "dark" : "light")
  }

  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem("stacy_theme", isDark.value ? "dark" : "light")
    apply()
  }

  return { isDark, init, toggle }
})
