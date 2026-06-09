import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchFolders, createFolder as apiCreateFolder, deleteFolderApi, fetchAssignments, assignCommandApi, unassignCommandApi } from '../api.js'

export const useFolderStore = defineStore('folders', () => {
  const folders = ref([])
  const commandFolders = ref({})
  const commandDescriptions = ref({})
  const selectedFolderId = ref('all')
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      const [resFolders, resAssignments] = await Promise.all([fetchFolders(), fetchAssignments()])
      folders.value = resFolders.carpetas || []
      commandFolders.value = {}
      commandDescriptions.value = {}
      ;(resAssignments.asignaciones || []).forEach(a => {
        if (!commandFolders.value[a.COM_ID]) commandFolders.value[a.COM_ID] = []
        commandFolders.value[a.COM_ID].push(a.CAR_ID)
        if (a.CC_DESCRIPCION) {
          commandDescriptions.value[a.CAR_ID + '_' + a.COM_ID] = a.CC_DESCRIPCION
        }
      })
    } catch (e) {
      console.error("Error cargando carpetas:", e)
    } finally {
      loading.value = false
    }
  }

  async function create(nombre, descripcion) {
    await apiCreateFolder(nombre, descripcion)
    await load()
  }

  async function remove(carId) {
    await deleteFolderApi(carId)
    await load()
  }

  function select(folderId) {
    selectedFolderId.value = folderId
  }

  async function setCommandFolders(comId, newCarIds) {
    const old = commandFolders.value[comId] || []
    const toAdd = newCarIds.filter(id => !old.includes(id))
    const toRemove = old.filter(id => !newCarIds.includes(id))
    for (const carId of toAdd) await assignCommandApi(comId, carId)
    for (const carId of toRemove) await unassignCommandApi(comId, carId)
    await load()
  }

  return { folders, commandFolders, commandDescriptions, selectedFolderId, loading, load, create, remove, select, setCommandFolders }
})
