import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchNotas, createNota as apiCreateNota, updateNota as apiUpdateNota, deleteNota as apiDeleteNota } from '../api.js'

export const useNoteStore = defineStore('notes', () => {
  const notas = ref([])
  const loading = ref(false)

  async function cargar() {
    loading.value = true
    try {
      const res = await fetchNotas()
      notas.value = res.notas || []
    } catch (e) {
      console.error("Error cargando notas:", e)
      notas.value = []
    } finally {
      loading.value = false
    }
  }

  async function create(titulo, contenido) {
    await apiCreateNota(titulo, contenido)
    await cargar()
  }

  async function update(notId, titulo, contenido) {
    await apiUpdateNota(notId, titulo, contenido)
    await cargar()
  }

  async function remove(notId) {
    await apiDeleteNota(notId)
    await cargar()
  }

  return { notas, loading, cargar, create, update, remove }
})
