<template>
  <main class="min-h-screen p-4 md:p-8">
    <div v-if="!roomStore.room" class="flex min-h-screen items-center justify-center">
      <p class="text-gray-500">Loading room…</p>
    </div>

    <div v-else class="max-w-4xl mx-auto space-y-8">
      <!-- Header -->
      <header class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">{{ roomStore.room.name }}</h1>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500">Round {{ roomStore.currentRound?.number }}</span>
          <button @click="copyInviteLink" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
            Copy invite link
          </button>
        </div>
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
              'h-20 w-14 rounded-xl border-2 text-lg font-bold transition-all',
              myVote === card
                ? 'border-indigo-500 bg-indigo-600 text-white scale-110 shadow-lg'
                : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-indigo-400 hover:scale-105',
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
          class="rounded-lg bg-green-600 px-5 py-2 font-semibold text-white hover:bg-green-700 transition-colors"
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
        <ul class="space-y-2">
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const userStore = useUserStore()

const error = ref('')
const roomId = route.params.roomId

const myVote = computed(() => {
  const me = roomStore.room?.participants?.[userStore.participantId]
  return me?.vote ?? null
})

const isOwner = computed(() => {
  const me = roomStore.room?.participants?.[userStore.participantId]
  return me?.is_owner ?? false
})

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
  try {
    await apiFetch(`/api/rooms/${roomId}/vote`, 'POST', {
      participant_id: userStore.participantId,
      card: newCard,
    })
    if (roomStore.room?.participants?.[userStore.participantId]) {
      roomStore.room.participants[userStore.participantId].vote = newCard ?? null
    }
  } catch (e) {
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
