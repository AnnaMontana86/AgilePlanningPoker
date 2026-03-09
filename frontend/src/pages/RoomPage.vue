<template>
  <main class="min-h-screen p-4 md:p-8">
    <div v-if="!roomStore.room" class="flex min-h-screen items-center justify-center">
      <p class="text-gray-500">Loading room…</p>
    </div>

    <div v-else class="max-w-4xl mx-auto space-y-8">
      <!-- Header -->
      <header class="flex items-center gap-4">
        <h1 class="text-2xl font-bold">{{ roomStore.room.name }}</h1>
        <button
          @click="copyInviteLink"
          title="Copy Invite Link"
          class="flex items-center gap-1.5 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
          </svg>
          Share
        </button>
        <button
          @click="leaveRoom"
          title="Leave Room"
          class="flex items-center gap-1.5 rounded-lg border border-red-300 dark:border-red-700 px-3 py-1.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h7a1 1 0 000-2H4V5h6a1 1 0 000-2H3zm11.293 4.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L15.586 11H9a1 1 0 010-2h6.586l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
          Leave
        </button>
        <span class="flex-1 text-center text-2xl font-semibold text-gray-600 dark:text-gray-300">
          Round {{ roomStore.currentRound?.number }}
        </span>
      </header>

      <!-- Card deck -->
      <section v-if="!roomStore.isRevealed">
        <h2 class="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wide">Your vote</h2>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="card in roomStore.cardSet?.cards"
            :key="card"
            @click="vote(card)"
            :class="[
              'h-20 w-14 rounded-xl border-2 text-lg font-bold transition-all bg-white dark:bg-gray-800',
              myVote === card
                ? 'border-blue-900 dark:border-blue-800'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-400',
            ]"
          >
            {{ card }}
          </button>
        </div>
      </section>

      <!-- Owner controls -->
      <section v-if="isOwner" class="flex gap-3 flex-wrap">
        <button
          v-if="!roomStore.isRevealed"
          @click="reveal"
          :disabled="!allVoted"
          class="rounded-lg bg-green-600 px-5 py-2 font-semibold text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Reveal Cards
        </button>
        <button
          v-if="roomStore.isRevealed"
          @click="newRound"
          class="rounded-lg bg-indigo-600 px-5 py-2 font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          New Round
        </button>
      </section>

      <!-- Participants -->
      <section>
        <h2 class="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wide">Participants</h2>
        <ul class="grid grid-cols-2 gap-2">
          <li
            v-for="p in roomStore.participants"
            :key="p.id"
            class="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3"
          >
            <span class="font-medium">
              {{ p.nickname }}
              <span v-if="p.is_owner" class="ml-2 text-xs text-indigo-500">owner</span>
            </span>
            <span class="flex items-center gap-3">
              <span :class="voteLabel(p).class">{{ voteLabel(p).text }}</span>
              <button
                v-if="isOwner && !p.is_owner"
                @click="kick(p.id)"
                class="text-xs text-red-500 hover:underline"
              >
                kick
              </button>
            </span>
          </li>
        </ul>
      </section>

      <!-- Results after reveal -->
      <section v-if="roomStore.isRevealed" class="rounded-xl border border-gray-200 dark:border-gray-700 p-4">
        <h2 class="mb-3 font-semibold">Results</h2>
        <p v-if="numericAverage !== null" class="text-sm text-gray-500">
          Average: <span class="font-bold text-gray-900 dark:text-gray-100">{{ numericAverage }}</span>
        </p>
      </section>

      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const userStore = useUserStore()

const error = ref('')
const roomId = route.params.roomId

const myVote = ref(null)

// Reset local vote when a new round starts
watch(() => roomStore.currentRound?.number, () => { myVote.value = null })

const isOwner = computed(() => {
  const me = roomStore.room?.participants?.[userStore.participantId]
  return me?.is_owner ?? false
})

const allVoted = computed(() =>
  roomStore.participants.length > 0 && roomStore.participants.every(p => p.vote)
)

const numericAverage = computed(() => {
  if (!roomStore.isRevealed) return null
  const nums = roomStore.participants
    .map(p => parseFloat(p.vote))
    .filter(n => !isNaN(n))
  if (!nums.length) return null
  return (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(1)
})

function voteLabel(participant) {
  if (!roomStore.isRevealed) {
    if (participant.vote) return { text: '✓', class: 'text-green-500 font-bold' }
    return { text: '…', class: 'text-gray-400' }
  }
  return { text: participant.vote ?? '–', class: 'font-bold' }
}

async function apiFetch(path, method = 'POST', body = {}) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: userStore.token, ...body }),
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText)
  return res.json()
}

async function vote(card) {
  error.value = ''
  const newCard = myVote.value === card ? null : card
  myVote.value = newCard
  try {
    await apiFetch(`/api/rooms/${roomId}/vote`, 'POST', {
      participant_id: userStore.participantId,
      card: newCard,
    })
  } catch (e) {
    myVote.value = newCard === null ? card : null // revert on error
    error.value = e.message
  }
}

async function reveal() {
  try { await apiFetch(`/api/rooms/${roomId}/reveal`) } catch (e) { error.value = e.message }
}

async function newRound() {
  try { await apiFetch(`/api/rooms/${roomId}/new-round`) } catch (e) { error.value = e.message }
}

async function kick(participantId) {
  try {
    await apiFetch(`/api/rooms/${roomId}/participants/${participantId}`, 'DELETE')
  } catch (e) { error.value = e.message }
}

async function leaveRoom() {
  try {
    await apiFetch(`/api/rooms/${roomId}/leave`, 'POST', {
      participant_id: userStore.participantId,
    })
  } finally {
    roomStore.clear()
    userStore.clearSession()
    router.push({ name: 'home' })
  }
}

function copyInviteLink() {
  navigator.clipboard.writeText(window.location.href)
}

onMounted(async () => {
  try {
    const res = await fetch(`/api/rooms/${roomId}`)
    if (!res.ok) { router.push({ name: 'home' }); return }
    roomStore.setRoom(await res.json())
    roomStore.connectSSE(roomId)
  } catch {
    router.push({ name: 'home' })
  }
})

onUnmounted(() => {
  roomStore.clear()
})
</script>
