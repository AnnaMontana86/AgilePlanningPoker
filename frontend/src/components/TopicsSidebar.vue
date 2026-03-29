<template>
  <aside
    v-if="roomStore.topics.length > 0 || isOwner"
    :class="[
      'flex flex-col border-t border-gray-200 dark:border-gray-700 lg:border-t-0 lg:flex-shrink-0',
      topicsOpen ? 'lg:w-[26.5rem] xl:w-[32rem]' : 'lg:w-10',
    ]"
  >
    <!-- Header row: toggle + label + download -->
    <div class="flex items-center gap-2 px-4 py-4">
      <button
        @click="topicsOpen = !topicsOpen"
        :title="topicsOpen ? 'Hide topics' : 'Show topics'"
        class="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
      >
        <!-- › when open (collapse), ‹ when closed (expand) -->
        <svg v-if="topicsOpen" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
      <h3 v-if="topicsOpen" class="flex-1 text-sm font-medium text-gray-500 uppercase tracking-wide">Topics</h3>
      <button
        v-if="topicsOpen && roomStore.topics.length > 0"
        @click="downloadCsv"
        title="Download CSV"
        class="rounded p-1 text-gray-400 hover:text-indigo-500 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <!-- Collapsible content -->
    <div v-if="topicsOpen" class="px-4 pb-4">
      <!-- Topic list -->
      <ol class="space-y-2">
        <li
          v-for="(topic, idx) in roomStore.topics"
          :key="topic.id"
          :class="topicItemClass(topic, idx)"
          :draggable="isOwner"
          @dragstart="onDragStart(idx)"
          @dragover.prevent="onDragOver(idx)"
          @drop.prevent="onDrop()"
          @dragend="onDragEnd()"
          @click="isOwner && idx !== roomStore.currentTopicIndex && selectTopic(topic.id)"
        >
          <!-- Drag handle (owner only) -->
          <svg
            v-if="isOwner"
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 shrink-0 cursor-grab text-gray-300 dark:text-gray-600 hover:text-gray-400 dark:hover:text-gray-400"
            viewBox="0 0 20 20" fill="currentColor"
            @mousedown.stop
          >
            <path d="M7 4a1 1 0 110-2 1 1 0 010 2zm6 0a1 1 0 110-2 1 1 0 010 2zM7 9a1 1 0 110-2 1 1 0 010 2zm6 0a1 1 0 110-2 1 1 0 010 2zm-6 5a1 1 0 110-2 1 1 0 010 2zm6 0a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
          <span class="w-5 text-xs text-gray-400 shrink-0">{{ idx + 1 }}</span>
          <span
            v-if="idx === roomStore.currentTopicIndex"
            class="h-2 w-2 rounded-full bg-indigo-500 shrink-0"
          ></span>
          <span class="flex-1 min-w-0 truncate">
            <a
              v-if="topic.link"
              :href="topic.link"
              target="_blank"
              rel="noopener"
              class="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
              @click.stop
            ><span class="font-mono">{{ topic.key }}</span><span v-if="topic.key">: </span><span class="text-gray-500 dark:text-gray-400">{{ topic.headline }}</span></a>
            <span v-else class="text-sm font-medium"><span class="font-mono">{{ topic.key }}</span><span v-if="topic.key">: </span><span class="text-gray-500 dark:text-gray-400">{{ topic.headline }}</span></span>
          </span>
          <!-- Estimated badge -->
          <span v-if="topic.estimates != null" class="flex items-center gap-1 shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span
              v-for="e in compactEstimates(topic.estimates)"
              :key="e.label"
              class="rounded-full bg-green-100 dark:bg-green-900/40 px-1.5 py-0.5 text-xs font-medium"
            ><span class="text-green-700 dark:text-green-300">{{ e.value }}</span><span v-if="e.count > 1" class="text-gray-500 dark:text-gray-400">({{ e.count }}x)</span></span>
          </span>
          <div v-if="isOwner" class="flex items-center gap-1 shrink-0" @click.stop>
            <button
              @click="openEditTopic(topic)"
              class="rounded p-1 text-gray-400 hover:text-indigo-500 transition-colors"
              title="Edit topic"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
            </button>
            <button
              @click="deleteTopic(topic.id)"
              class="rounded p-1 text-red-400 hover:text-red-600 transition-colors"
              title="Remove topic"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </li>
      </ol>

      <!-- Add topic inline form -->
      <div v-if="isOwner && showAddTopic" class="mt-3 space-y-2">
        <div class="flex gap-2">
          <input
            v-model="newTopicKey"
            placeholder="Key"
            @keydown.enter="addTopic"
            class="w-28 shrink-0 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="newTopicHeadline"
            placeholder="Headline"
            @keydown.enter="addTopic"
            class="flex-1 min-w-0 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <input
          v-model="newTopicLink"
          placeholder="Link (optional)"
          @keydown.enter="addTopic"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <div class="flex gap-2">
          <button
            @click="addTopic"
            :disabled="!newTopicKey.trim() || !newTopicHeadline.trim()"
            class="flex-1 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >Add</button>
          <button
            @click="showAddTopic = false"
            class="rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >Cancel</button>
        </div>
      </div>

      <!-- + button at bottom of topic list -->
      <button
        v-if="isOwner && !showAddTopic"
        @click="showAddTopic = true"
        class="mt-3 w-full rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 py-2 text-sm text-gray-400 dark:text-gray-500 hover:border-indigo-400 hover:text-indigo-500 dark:hover:border-indigo-500 dark:hover:text-indigo-400 transition-colors"
      >+</button>
    </div><!-- end collapsible content -->

    <!-- Edit topic dialog -->
    <EditTopicDialog
      :topic="editingTopic"
      @save="({ key, headline, link }) => saveEditTopic(editingTopic.id, { key, headline, link })"
      @cancel="editingTopic = null"
    />
  </aside>
</template>

<script setup>
// Collapsible sidebar listing the room's topics with owner controls.
// Responsible for topic selection, reordering, editing, deletion, and CSV export of estimates.
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'
import { useTopics } from '../composables/useTopics'
import { useVoteAnalysis } from '../composables/useVoteAnalysis'
import EditTopicDialog from './EditTopicDialog.vue'

const props = defineProps({ isOwner: Boolean })

const route = useRoute()
const roomId = route.params.roomId
const roomStore = useRoomStore()
const userStore = useUserStore()
const error = ref('')
const topicsOpen = ref(true)

async function apiFetch(path, method = 'POST', body = {}) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: userStore.token, ...body }),
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText)
  return res.json()
}

const { showAddTopic, newTopicKey, newTopicHeadline, newTopicLink, editingTopic,
        addTopic, reorderTopics, deleteTopic, selectTopic, openEditTopic, saveEditTopic } =
  useTopics(roomId, roomStore, apiFetch, error)

const dragFromIdx = ref(null)
const dragOverIdx = ref(null)

function onDragStart(idx) { dragFromIdx.value = idx }
function onDragOver(idx) { dragOverIdx.value = idx }
function onDrop() {
  if (dragFromIdx.value !== null && dragOverIdx.value !== null) {
    reorderTopics(dragFromIdx.value, dragOverIdx.value)
  }
  dragFromIdx.value = null
  dragOverIdx.value = null
}
function onDragEnd() {
  dragFromIdx.value = null
  dragOverIdx.value = null
}

const { compactEstimates } = useVoteAnalysis(roomStore)

function downloadCsv() {
  const topics = roomStore.topics

  // Collect all unique participant nicknames that appear in any estimated topic
  const nicknameSet = new Set()
  for (const topic of topics) {
    if (topic.participant_votes) {
      for (const nickname of Object.keys(topic.participant_votes)) {
        nicknameSet.add(nickname)
      }
    }
  }
  const nicknames = [...nicknameSet].sort()

  const header = ['Key', 'Headline', 'Link', ...nicknames]

  const rows = topics.map(topic => {
    const perUser = nicknames.map(n => topic.participant_votes?.[n] ?? '')
    return [topic.key, topic.headline, topic.link ?? '', ...perUser]
  })

  // Semicolon delimiter avoids conflicts with comma-containing card values;
  // cells containing semicolons, quotes, or newlines are RFC 4180 quoted.
  const encodeCell = cell => {
    const s = String(cell)
    return (s.includes(';') || s.includes('"') || s.includes('\n'))
      ? `"${s.replace(/"/g, '""')}"`
      : s
  }
  const csv = [header, ...rows].map(row => row.map(encodeCell).join(';')).join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${roomStore.room?.name ?? 'planning-poker'}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function topicItemClass(topic, idx) {
  const base = 'flex items-center gap-3 rounded-lg border px-4 py-2.5 bg-white dark:bg-gray-800 transition-colors'
  const isDragOver = props.isOwner && dragOverIdx.value === idx && dragFromIdx.value !== idx
  const active = isDragOver
    ? 'border-indigo-400 dark:border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
    : idx === roomStore.currentTopicIndex
      ? 'border-indigo-400 dark:border-indigo-500'
      : 'border-gray-200 dark:border-gray-700'
  const dragging = props.isOwner && dragFromIdx.value === idx ? 'opacity-40' : ''
  const clickable = props.isOwner && idx !== roomStore.currentTopicIndex
    ? 'cursor-pointer hover:border-indigo-300 dark:hover:border-indigo-600'
    : ''
  return `${base} ${active} ${dragging} ${clickable}`
}
</script>
