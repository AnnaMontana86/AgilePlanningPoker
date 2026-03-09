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
          @input="nicknameError = false"
          type="text"
          maxlength="32"
          placeholder="Enter your nickname"
          :class="[
            'w-full rounded-lg border bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 transition-colors',
            nicknameError
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 dark:border-gray-600 focus:ring-indigo-500'
          ]"
        />
        <p v-if="nicknameError" class="text-red-500 text-sm">Please enter a nickname first.</p>
      </section>

      <!-- Action Buttons -->
      <div class="flex gap-4">
        <button
          @click="nickname.trim() ? (showCreate = true) : (nicknameError = true)"
          class="flex-1 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Create a room
        </button>
        <button
          @click="nickname.trim() ? (showJoin = true) : (nicknameError = true)"
          class="flex-1 flex items-center justify-center gap-2 rounded-xl border border-indigo-600 px-4 py-3 font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V7.414A1 1 0 0015.707 7l-4-4A1 1 0 0011 2.586V2H4a1 1 0 00-1 1zm9 1.414L14.586 7H12V4.414zM4 4h7v4a1 1 0 001 1h4v8H4V4z" clip-rule="evenodd" />
            <path d="M7 9a1 1 0 000 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7a1 1 0 10-2 0v2H7z" />
          </svg>
          Join a room
        </button>
      </div>

      <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
    </div>

    <!-- Create Room Dialog -->
    <Teleport to="body">
      <div
        v-if="showCreate"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showCreate = false"
      >
        <div class="w-full max-w-sm rounded-2xl bg-white dark:bg-gray-900 shadow-xl p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Create a room</h2>
            <button @click="showCreate = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
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
            <option v-for="(cards, name) in cardSets" :key="name" :value="name">
            {{ name }} ({{ cards.slice(0, 5).join(', ') }}{{ cards.length > 5 ? ', …' : '' }})
          </option>
          </select>
          <button
            :disabled="!canCreate"
            @click="createRoom"
            class="w-full rounded-lg bg-indigo-600 px-4 py-2 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Create Room
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Join Room Dialog -->
    <Teleport to="body">
      <div
        v-if="showJoin"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showJoin = false"
      >
        <div class="w-full max-w-sm rounded-2xl bg-white dark:bg-gray-900 shadow-xl p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Join a room</h2>
            <button @click="showJoin = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
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
        </div>
      </div>
    </Teleport>
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
const showCreate = ref(false)
const showJoin = ref(false)
const nicknameError = ref(false)

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

  if (route.query.redirect) {
    showJoin.value = true
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
    showCreate.value = false
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
    showJoin.value = false
  }
}
</script>
