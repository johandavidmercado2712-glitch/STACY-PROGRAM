import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchComandos } from '../api.js'
import { extractMaquina } from '../helpers/utils.js'
import { getCookie, setCookie } from '../helpers/cookie.js'

export const useCommandStore = defineStore('commands', () => {
  const comandosCache = ref([])
  const vistaActual = ref('all')
  const selectedFolderId = ref('all')
  const selectedMaquina = ref('all')
  const loading = ref(false)
  const error = ref('')

  const maquinasDisponibles = computed(() => {
    const set = new Set()
    comandosCache.value.forEach(c => {
      const m = extractMaquina(c.ruta)
      if (m) set.add(m)
    })
    return [...set]
  })

  const filteredComandos = computed(() => {
    let pool = vistaActual.value === 'recent' ? comandosCache.value.slice(0, 11) : comandosCache.value
    if (selectedMaquina.value && selectedMaquina.value !== 'all') {
      pool = pool.filter(c => extractMaquina(c.ruta) === selectedMaquina.value)
    }
    return pool
  })

  const seen = new Set()
  async function cargar() {
    loading.value = true
    error.value = ''
    try {
      const res = await fetchComandos()
      const raw = res.comandos || []
      seen.clear()
      comandosCache.value = raw.filter(c => {
        if (!c.com_id || seen.has(c.com_id)) return false
        seen.add(c.com_id)
        return true
      })
      const saved = getCookie("stacy_maquina")
      if (saved && maquinasDisponibles.value.includes(saved)) {
        selectedMaquina.value = saved
      } else {
        selectedMaquina.value = 'all'
      }
    } catch (e) {
      error.value = 'No se pudo conectar al backend.'
      comandosCache.value = []
    } finally {
      loading.value = false
    }
  }

  function setVista(vista) {
    vistaActual.value = vista
  }

  function selectMaquina(maquina) {
    selectedMaquina.value = maquina
    setCookie("stacy_maquina", maquina)
  }

  function selectFolder(folderId) {
    selectedFolderId.value = folderId
  }

  return { comandosCache, vistaActual, selectedFolderId, selectedMaquina, loading, error, maquinasDisponibles, filteredComandos, cargar, setVista, selectMaquina, selectFolder }
})
