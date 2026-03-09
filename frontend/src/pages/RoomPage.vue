<template>
  <div class="min-h-screen flex flex-col">
    <div v-if="!roomStore.room" class="flex flex-1 items-center justify-center">
      <p class="text-gray-500">Loading room…</p>
    </div>

    <template v-else>
      <!-- Toolbar -->
      <header class="sticky top-0 z-10 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-2 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <!-- Left: room title -->
        <h1 class="text-lg font-bold truncate">{{ roomStore.room.name }}</h1>

        <!-- Center: active countdown -->
        <span
          v-if="timerRemaining !== null"
          :class="[
            'text-xl font-mono font-bold tabular-nums',
            timerRemaining <= 10 ? 'text-red-500' : 'text-gray-700 dark:text-gray-200',
          ]"
        >{{ formattedTimer }}</span>
        <span v-else></span>

        <!-- Right: action buttons -->
        <div class="flex items-center gap-3 justify-end">

        <!-- Share -->
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

        <!-- Timer (owner only) -->
        <button
          v-if="isOwner"
          @click="timerDialog = true"
          title="Set Timer"
          class="flex items-center gap-1.5 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
          Timer
        </button>

        <!-- Leave -->
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

        <!-- Theme toggle -->
        <button
          @click="themeStore.toggle()"
          class="rounded-full p-1.5 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow transition-all"
          :aria-label="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <svg v-if="themeStore.isDark" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-yellow-400" viewBox="0 0 122.88 122.88" fill="currentColor">
            <path fill-rule="evenodd" d="M30,13.21A3.93,3.93,0,1,1,36.8,9.27L41.86,18A3.94,3.94,0,1,1,35.05,22L30,13.21Zm31.45,13A35.23,35.23,0,1,1,36.52,36.52,35.13,35.13,0,0,1,61.44,26.2ZM58.31,4A3.95,3.95,0,1,1,66.2,4V14.06a3.95,3.95,0,1,1-7.89,0V4ZM87.49,10.1A3.93,3.93,0,1,1,94.3,14l-5.06,8.76a3.93,3.93,0,1,1-6.81-3.92l5.06-8.75ZM109.67,30a3.93,3.93,0,1,1,3.94,6.81l-8.75,5.06a3.94,3.94,0,1,1-4-6.81L109.67,30Zm9.26,28.32a3.95,3.95,0,1,1,0,7.89H108.82a3.95,3.95,0,1,1,0-7.89Zm-6.15,29.18a3.93,3.93,0,1,1-3.91,6.81l-8.76-5.06A3.93,3.93,0,1,1,104,82.43l8.75,5.06ZM92.89,109.67a3.93,3.93,0,1,1-6.81,3.94L81,104.86a3.94,3.94,0,0,1,6.81-4l5.06,8.76Zm-28.32,9.26a3.95,3.95,0,1,1-7.89,0V108.82a3.95,3.95,0,1,1,7.89,0v10.11Zm-29.18-6.15a3.93,3.93,0,0,1-6.81-3.91l5.06-8.76A3.93,3.93,0,1,1,40.45,104l-5.06,8.75ZM13.21,92.89a3.93,3.93,0,1,1-3.94-6.81L18,81A3.94,3.94,0,1,1,22,87.83l-8.76,5.06ZM4,64.57a3.95,3.95,0,1,1,0-7.89H14.06a3.95,3.95,0,1,1,0,7.89ZM10.1,35.39A3.93,3.93,0,1,1,14,28.58l8.76,5.06a3.93,3.93,0,1,1-3.92,6.81L10.1,35.39Z" clip-rule="evenodd" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        </button>

        </div><!-- end right buttons -->
      </header>

      <!-- Page body -->
      <main class="flex-1 max-w-4xl w-full mx-auto px-4 py-8 space-y-8">

        <!-- Round headline -->
        <h2 class="text-center text-3xl font-semibold text-gray-600 dark:text-gray-300">
          Round {{ roomStore.currentRound?.number }}
        </h2>

        <!-- Owner action (centered) -->
        <div v-if="isOwner" class="flex justify-center">
          <button
            v-if="!roomStore.isRevealed"
            @click="reveal"
            :disabled="!allVoted"
            class="rounded-lg bg-green-600 px-8 py-2.5 font-semibold text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Reveal Cards
          </button>
          <button
            v-if="roomStore.isRevealed"
            @click="newRound"
            class="rounded-lg bg-indigo-600 px-8 py-2.5 font-semibold text-white hover:bg-indigo-700 transition-colors"
          >
            New Round
          </button>
        </div>

        <!-- Participants -->
        <section>
          <h3 class="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wide">Participants</h3>
          <ul class="grid grid-cols-2 gap-2">
            <li
              v-for="p in roomStore.participants"
              :key="p.id"
              :class="[
                'flex items-center justify-between rounded-lg border bg-white dark:bg-gray-800 px-4 py-3',
                !roomStore.isRevealed && p.vote
                  ? 'border-green-400 dark:border-green-500'
                  : 'border-gray-200 dark:border-gray-700'
              ]"
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
          <!-- Results after reveal -->
          <p v-if="roomStore.isRevealed && numericAverage !== null" class="mt-3 text-sm text-gray-500 text-center">
            Average: <span class="font-bold text-gray-900 dark:text-gray-100">{{ numericAverage }}</span>
          </p>
        </section>

        <!-- Card selection (centered) -->
        <section v-if="!roomStore.isRevealed" class="flex flex-col items-center gap-3">
          <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Your vote</h3>
          <div class="flex flex-wrap justify-center gap-3">
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

        <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
      </main>

      <!-- Copy toast -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-2"
      >
        <div
          v-if="copyToast"
          class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 rounded-xl bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 px-4 py-2.5 text-sm font-medium shadow-lg pointer-events-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-400 dark:text-green-600" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          Invite link copied!
        </div>
      </Transition>

      <!-- Fireworks canvas -->
      <canvas
        ref="fireworksCanvas"
        class="fixed inset-0 z-40 pointer-events-none"
        :style="{ display: fireworksActive ? 'block' : 'none' }"
      />

      <!-- Timer dialog -->
      <div
        v-if="timerDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="timerDialog = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-96 space-y-5">
          <h3 class="text-lg font-semibold">Set Timer</h3>

          <div class="flex gap-3">
            <input
              v-model.number="timerInput"
              type="number"
              min="1"
              placeholder="Duration"
              class="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <select
              v-model="timerUnit"
              class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="seconds">sec</option>
              <option value="minutes">min</option>
            </select>
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="timerDialog = false"
              class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >Cancel</button>
            <button
              @click="startTimer"
              :disabled="!timerInput || timerInput < 1"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >Start</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const userStore = useUserStore()
const themeStore = useThemeStore()

const error = ref('')
const roomId = route.params.roomId

// Timer
const timerDialog = ref(false)
const timerInput = ref(null)
const timerUnit = ref('minutes')
const timerRemaining = ref(null)
let timerInterval = null

const formattedTimer = computed(() => {
  if (timerRemaining.value === null) return ''
  const m = Math.floor(timerRemaining.value / 60)
  const s = timerRemaining.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function startTimer() {
  if (!timerInput.value || timerInput.value < 1) return
  const seconds = timerUnit.value === 'minutes' ? timerInput.value * 60 : timerInput.value
  timerRemaining.value = seconds
  timerDialog.value = false
  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    timerRemaining.value--
    if (timerRemaining.value <= 0) {
      timerRemaining.value = 0
      clearInterval(timerInterval)
    }
  }, 1000)
}

const myVote = ref(null)

// Reset local vote when a new round starts
watch(() => roomStore.currentRound?.number, () => { myVote.value = null })

// Fireworks
const fireworksCanvas = ref(null)
const fireworksActive = ref(false)
let fireworksRaf = null

const allSameVote = computed(() => {
  if (!roomStore.isRevealed) return false
  const votes = roomStore.participants.map(p => p.vote).filter(v => v != null)
  return votes.length >= 2 && votes.every(v => v === votes[0])
})

watch(allSameVote, (same) => {
  if (same) nextTick(launchFireworks)
})

function launchFireworks() {
  fireworksActive.value = true
  const canvas = fireworksCanvas.value
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  const ctx = canvas.getContext('2d')
  const particles = []
  const COLORS = ['#ff4444','#ff8800','#ffdd00','#44ff44','#44aaff','#aa44ff','#ff44aa','#ffffff']
  const DURATION = 4000
  const start = performance.now()

  function spawnBurst() {
    const x = 0.2 * canvas.width + Math.random() * 0.6 * canvas.width
    const y = 0.1 * canvas.height + Math.random() * 0.45 * canvas.height
    const color = COLORS[Math.floor(Math.random() * COLORS.length)]
    const count = 80 + Math.floor(Math.random() * 40)
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.3
      const speed = 2 + Math.random() * 5
      particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        alpha: 1,
        color,
        radius: 2 + Math.random() * 2,
      })
    }
  }

  let lastBurst = 0
  function frame(now) {
    const elapsed = now - start
    if (elapsed > DURATION) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      fireworksActive.value = false
      return
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (now - lastBurst > 600) {
      spawnBurst()
      lastBurst = now
    }

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i]
      p.x += p.vx
      p.y += p.vy
      p.vy += 0.08  // gravity
      p.vx *= 0.98  // drag
      p.alpha -= 0.013
      if (p.alpha <= 0) { particles.splice(i, 1); continue }
      ctx.globalAlpha = p.alpha
      ctx.fillStyle = p.color
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fill()
    }
    ctx.globalAlpha = 1
    fireworksRaf = requestAnimationFrame(frame)
  }

  spawnBurst()
  fireworksRaf = requestAnimationFrame(frame)
}

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
    if (participant.vote) return { text: '✓', class: 'text-green-500 font-bold text-xl' }
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

const copyToast = ref(false)
let copyToastTimer = null

function copyInviteLink() {
  navigator.clipboard.writeText(window.location.href)
  if (copyToastTimer) clearTimeout(copyToastTimer)
  copyToast.value = true
  copyToastTimer = setTimeout(() => { copyToast.value = false }, 2000)
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

onBeforeUnmount(() => {
  clearInterval(timerInterval)
  cancelAnimationFrame(fireworksRaf)
  clearTimeout(copyToastTimer)
})

onUnmounted(() => {
  roomStore.clear()
})
</script>
