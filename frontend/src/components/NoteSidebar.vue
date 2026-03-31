<template>
  <aside
    v-if="isOwner || roomStore.room?.note"
    :class="[
      'flex flex-col border-b border-gray-200 dark:border-gray-700 lg:border-b-0 lg:flex-shrink-0 order-first',
      noteOpen ? 'lg:w-52 xl:w-64' : 'lg:w-10',
    ]"
  >
    <!-- Header row: label + owner edit + toggle -->
    <div class="flex items-center gap-2 px-4 py-4">
      <span v-if="noteOpen" class="flex-1 text-sm font-medium text-gray-500 uppercase tracking-wide">Note</span>
      <button
        v-if="isOwner && noteOpen && !noteEditing"
        @click="startEditNote"
        class="rounded p-1 text-gray-400 hover:text-amber-500 transition-colors"
        title="Edit note"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
        </svg>
      </button>
      <!-- ‹ to collapse (left sidebar), › to expand -->
      <button
        @click="noteOpen = !noteOpen"
        :title="noteOpen ? 'Hide note' : 'Show note'"
        class="ml-auto rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
      >
        <svg v-if="noteOpen" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- Collapsible content -->
    <div v-if="noteOpen" class="px-4 pb-4 flex-1 flex flex-col gap-3">
      <!-- Edit mode -->
      <div
        v-if="noteEditing"
        class="space-y-2 relative"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
      >
        <!-- Drop-zone overlay -->
        <div
          v-if="isDragOver"
          class="absolute inset-0 z-10 flex items-center justify-center rounded-lg border-2 border-dashed border-amber-400 bg-amber-50/80 dark:bg-amber-900/40 pointer-events-none"
        >
          <span class="text-sm font-medium text-amber-600 dark:text-amber-300">Drop image here</span>
        </div>
        <p v-if="uploading" class="text-xs text-gray-400">Uploading image…</p>
        <textarea
          v-model="noteDraft"
          rows="8"
          placeholder="Write a note for all participants… (markdown supported, drop images here)"
          class="w-full rounded-lg border border-amber-300 dark:border-amber-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 resize-y"
        />
        <div class="flex gap-2 justify-end">
          <button
            @click="cancelNote"
            class="rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >Cancel</button>
          <button
            @click="saveNote"
            class="rounded-lg bg-amber-500 px-3 py-1.5 text-sm font-semibold text-white hover:bg-amber-600 transition-colors"
          >Save</button>
        </div>
      </div>
      <!-- Display mode -->
      <div v-else>
        <button
          v-if="isOwner && !roomStore.room?.note"
          @click="startEditNote"
          class="text-sm text-gray-400 dark:text-gray-500 hover:text-amber-500 dark:hover:text-amber-400 transition-colors"
        >Add a note for all participants…</button>
        <div
          v-else-if="roomStore.room?.note"
          class="prose prose-sm dark:prose-invert max-w-none"
          v-html="renderedNote"
        />
      </div>
    </div>
  </aside>
</template>

<script setup>
// Collapsible sidebar for the shared room note.
// Responsible for rendering the markdown note as sanitised HTML,
// providing the owner with an inline edit interface, and supporting
// drag-and-drop image upload into the note.
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'
import { useNote } from '../composables/useNote'
import { useImageUpload } from '../composables/useImageUpload'

defineProps({ isOwner: Boolean })

const route = useRoute()
const roomId = route.params.roomId
const roomStore = useRoomStore()
const userStore = useUserStore()
const error = ref('')

async function apiFetch(path, method = 'POST', body = {}) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: userStore.token, ...body }),
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText)
  return res.json()
}

const { noteOpen, noteEditing, noteDraft, renderedNote, startEditNote, cancelNote, saveNote, insertImageMarkdown } =
  useNote(roomId, roomStore, apiFetch, error)

const { uploading, uploadImage } = useImageUpload(roomId, apiFetch, error)
const isDragOver = ref(false)

async function handleDrop(event) {
  event.preventDefault()
  isDragOver.value = false
  for (const file of Array.from(event.dataTransfer?.files ?? []).filter(f => f.type.startsWith('image/'))) {
    const url = await uploadImage(file)
    if (url) insertImageMarkdown(url)
  }
}

function handleDragOver(e) {
  e.preventDefault()
  isDragOver.value = true
}

function handleDragLeave() {
  isDragOver.value = false
}
</script>

<style scoped>
:deep(.prose img) {
  display: inline-block;
  max-height: 80px;
  width: auto;
  border-radius: 4px;
  cursor: zoom-in;
  transition: max-height 0.2s ease, box-shadow 0.2s ease;
}
:deep(.prose img:hover) {
  max-height: 600px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 20;
}
</style>
