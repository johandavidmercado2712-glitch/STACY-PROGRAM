import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
  const visible = ref(false)
  const title = ref('')
  const bodyHTML = ref('')
  const footerActions = ref([])

  function open(t, body, actions = []) {
    title.value = t
    bodyHTML.value = body
    footerActions.value = actions
    visible.value = true
  }

  function close() {
    visible.value = false
    title.value = ''
    bodyHTML.value = ''
    footerActions.value = []
  }

  return { visible, title, bodyHTML, footerActions, open, close }
})
