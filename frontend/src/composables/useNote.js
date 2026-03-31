// Composable for the shared room note feature.
// Responsible for managing edit/display state and rendering the note
// as sanitised HTML via marked + DOMPurify.
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function useNote(roomId, roomStore, apiFetch, error) {
  const noteOpen = ref(true)
  const noteEditing = ref(false)
  const noteDraft = ref('')

  const renderedNote = computed(() => {
    const raw = roomStore.room?.note
    if (!raw) return ''
    return DOMPurify.sanitize(marked.parse(raw))
  })

  function startEditNote() {
    noteDraft.value = roomStore.room?.note ?? ''
    noteEditing.value = true
  }

  function cancelNote() {
    noteEditing.value = false
    noteDraft.value = ''
  }

  async function saveNote() {
    try {
      await apiFetch(`/api/rooms/${roomId}/note`, 'PATCH', { note: noteDraft.value || null })
      noteEditing.value = false
      noteDraft.value = ''
    } catch (e) { error.value = e.message }
  }

  function insertImageMarkdown(url) {
    noteDraft.value = (noteDraft.value ?? '') + `\n![](${url})\n`
  }

  return { noteOpen, noteEditing, noteDraft, renderedNote, startEditNote, cancelNote, saveNote, insertImageMarkdown }
}
