<template>
  <main class="flex min-h-screen items-center justify-center p-4">
    <div class="w-full max-w-md space-y-6">
      <h1 class="text-3xl font-bold text-center">Planning Poker</h1>

      <!-- Nickname -->
      <section class="space-y-2">
        <label class="block text-sm font-medium" for="nickname">Your nickname</label>
        <input
          id="nickname"
          v-model="nickname"
          type="text"
          maxlength="32"
          placeholder="Enter your nickname"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </section>

      <!-- Create Room -->
      <section class="space-y-3 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
        <h2 class="font-semibold">Create a room</h2>
        <input
          v-model="newRoomName"
          type="text"
          maxlength="80"
          placeholder="Room name"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <select
          v-model="selectedCardSet"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Select a card set</option>
          <option v-for="(_, name) in cardSets" :key="name" :value="name">{{ name }}</option>
        </select>
        <button
          :disabled="!canCreate"
          @click="createRoom"
          class="w-full rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Create Room
        </button>
      </section>

      <!-- Join Room -->
      <section class="space-y-3 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
        <h2 class="font-semibold">Join a room</h2>
        <input
          v-model="joinCode"
          type="text"
          placeholder="Room ID or paste invite link"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          :disabled="!canJoin"
          @click="joinRoom"
          class="w-full rounded-lg border border-indigo-600 px-4 py-2 font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Join Room
        </button>
      </section>

      <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const nickname = ref(userStore.nickname)
const newRoomName = ref('')
const selectedCardSet = ref('')
const joinCode = ref('')
const cardSets = ref({})
const error = ref('')

const canCreate = computed(() => nickname.value.trim() && newRoomName.value.trim() && selectedCardSet.value)
const canJoin = computed(() => nickname.value.trim() && joinCode.value.trim())

onMounted(async () => {
  try {
    const res = await fetch('/api/card-sets')
    if (!res.ok) throw new Error(`Server returned ${res.status}`)
    cardSets.value = await res.json()
  } catch {
    error.value = 'Could not load card sets. Is the server running?'
  }
})

async function createRoom() {
  error.value = ''
  userStore.setNickname(nickname.value.trim())
  try {
    const res = await fetch('/api/rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newRoomName.value.trim(),
        card_set_name: selectedCardSet.value,
        owner_nickname: userStore.nickname,
      }),
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    userStore.setSession(data.participant_id, data.token)
    router.push({ name: 'room', params: { roomId: data.room_id } })
  } catch (e) {
    error.value = `Failed to create room: ${e.message}`
  }
}

async function joinRoom() {
  error.value = ''
  userStore.setNickname(nickname.value.trim())
  const roomId = joinCode.value.trim().split('/').pop()
  try {
    const res = await fetch(`/api/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname: userStore.nickname }),
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    userStore.setSession(data.participant_id, data.token)
    router.push({ name: 'room', params: { roomId } })
  } catch (e) {
    error.value = `Failed to join room: ${e.message}`
  }
}
</script>
