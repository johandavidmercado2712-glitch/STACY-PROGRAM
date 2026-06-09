<script setup>
import { useNoteStore } from '../stores/notes.js'
import { useModalStore } from '../stores/modal.js'

const notes = useNoteStore()
const modal = useModalStore()

function escapeHtml(str) {
  if (!str) return ''
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function openEditor(nota) {
  modal.open(nota ? 'Editar nota' : 'Nueva nota', `
    <input type="text" id="modal-nota-title" class="w-full px-3 py-2.5 text-sm font-semibold bg-bg border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] box-border" placeholder="Titulo de la nota" value="${escapeHtml(nota ? nota.NOT_TITULO : '')}" />
    <textarea id="modal-nota-content" class="w-full min-h-[200px] px-3 py-2.5 text-sm bg-bg border border-border rounded-lg text-text outline-none transition-[border-color] focus:border-accent focus:shadow-[0_0_0_2px_var(--color-accent-dim)] box-border resize-vertical mt-2" placeholder="Escribe tu nota aqui...">${escapeHtml(nota ? nota.NOT_CONTENIDO : '')}</textarea>
  `, [
    nota ? { text: 'Eliminar', class: 'btn-sm btn-outline text-danger', action: async () => {
      if (!confirm('Eliminar esta nota?')) return
      await notes.remove(nota.NOT_ID)
      modal.close()
    }} : null,
    { text: 'Cancelar', class: 'btn-sm btn-outline', action: () => modal.close() },
    { text: 'Guardar', class: 'btn-sm', action: async () => {
      const title = document.getElementById('modal-nota-title').value.trim()
      const content = document.getElementById('modal-nota-content').value
      if (!title) return
      if (nota) await notes.update(nota.NOT_ID, title, content)
      else await notes.create(title, content)
      modal.close()
    }},
  ].filter(Boolean))
}

function formatRelTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr.replace(' ', 'T'))
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Ahora'
  if (mins < 60) return mins + 'm'
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return hrs + 'h'
  const days = Math.floor(hrs / 24)
  if (days < 7) return days + 'd'
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-xs font-bold uppercase tracking-wide text-text-secondary m-0 flex items-center gap-1.5">
        <lord-icon src="https://media.lordicon.com/assets/icons/editor/edit.json" class="current-color" trigger="hover" style="width:14px;height:14px"></lord-icon>
        Notas
      </h3>
      <button @click="openEditor(null)" class="w-7 h-7 bg-transparent border border-border text-text-secondary rounded-lg cursor-pointer text-lg leading-none flex items-center justify-center hover:bg-accent-dim hover:border-accent hover:text-accent hover:scale-108 active:scale-95 transition-all" type="button" title="Nueva nota">+</button>
    </div>
    <div v-if="notes.loading" class="text-center py-5 text-text-secondary text-sm">Cargando...</div>
    <div v-else-if="notes.notas.length === 0" class="text-center py-6 text-text-secondary text-sm">No tienes notas aun</div>
    <div v-else class="flex flex-col gap-1.5">
      <div v-for="n in notes.notas" :key="n.NOT_ID" @click="openEditor(n)" class="group relative flex items-start gap-3 px-3 py-2.5 bg-surface border border-border rounded-xl cursor-pointer transition-all hover:border-accent/30 hover:shadow-md hover:-translate-y-0.5">
        <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-accent-dim flex items-center justify-center mt-0.5">
          <lord-icon src="https://media.lordicon.com/assets/icons/editor/edit.json" trigger="hover" colors="primary:#f59e0b" style="width:15px;height:15px"></lord-icon>
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0 flex-1">
              <div class="text-sm font-semibold text-text truncate leading-tight">{{ n.NOT_TITULO || 'Sin titulo' }}</div>
              <div class="text-xs text-text-secondary mt-0.5 line-clamp-2 leading-relaxed">{{ (n.NOT_CONTENIDO || '').replace(/\n/g, ' ').substring(0, 80) || 'Sin contenido' }}</div>
            </div>
            <span class="text-[0.55rem] text-text-secondary/50 whitespace-nowrap flex-shrink-0 mt-0.5">{{ formatRelTime(n.NOT_UPDATED_AT) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
