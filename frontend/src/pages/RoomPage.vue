<template>
  <div class="min-h-screen flex flex-col">
    <div v-if="!roomStore.room" class="flex flex-1 items-center justify-center">
      <p class="text-gray-500">Loading room…</p>
    </div>

    <!-- Join overlay for share-link visitors -->
    <div
      v-else-if="joining"
      class="flex flex-1 items-center justify-center px-4"
    >
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 w-full max-w-sm space-y-5">
        <div>
          <h2 class="text-xl font-bold">Join {{ roomStore.room.name }}</h2>
          <p class="text-sm text-gray-500 mt-1">Enter your nickname to join this room.</p>
        </div>
        <input
          v-model="joinNickname"
          placeholder="Your nickname"
          @keydown.enter="joinRoom"
          autofocus
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p v-if="joinError" class="text-sm text-red-500">{{ joinError }}</p>
        <button
          @click="joinRoom"
          :disabled="!joinNickname.trim()"
          class="w-full rounded-lg bg-indigo-600 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >Join Room</button>
      </div>
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

        <!-- Mood button + dropdown -->
        <div class="relative" ref="moodAnchor">
          <button
            @click="moodOpen = !moodOpen"
            :class="[
              'flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors',
              moodOpen || myEmoji
                ? 'border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400',
            ]"
            title="Mood"
          >
            <span v-if="myEmoji" class="text-base leading-none">{{ myEmoji }}</span>
            <svg v-else class="h-4 w-4" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <mask id="mood-icon-mask">
                  <circle cx="510.944" cy="512" r="448" fill="white"/>
                  <path fill="black" d="M512 773.344c-89.184 0-171.904-40.32-226.912-110.624-10.88-13.92-8.448-34.016 5.472-44.896 13.888-10.912 34.016-8.48 44.928 5.472 42.784 54.688 107.136 86.048 176.512 86.048 70.112 0 134.88-31.904 177.664-87.552 10.784-14.016 30.848-16.672 44.864-5.888 14.016 10.784 16.672 30.88 5.888 44.864C685.408 732.32 602.144 773.344 512 773.344zM368 515.2c-26.528 0-48-21.472-48-48v-64c0-26.528 21.472-48 48-48s48 21.472 48 48v64c0 26.496-21.504 48-48 48zM656 515.2c-26.496 0-48-21.472-48-48v-64c0-26.528 21.504-48 48-48s48 21.472 48 48v64c0 26.496-21.504 48-48 48z"/>
                </mask>
              </defs>
              <circle cx="510.944" cy="512" r="448" fill="currentColor" mask="url(#mood-icon-mask)"/>
            </svg>
            <span class="hidden sm:inline">Mood</span>
          </button>
          <!-- Dropdown -->
          <div
            v-if="moodOpen"
            class="absolute left-0 top-full mt-1.5 z-20 flex flex-col sm:flex-row gap-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg px-2 py-1.5"
          >
            <button
              v-for="e in EMOJIS"
              :key="e"
              @click="setEmoji(e); moodOpen = false"
              :title="e"
              :class="[
                'text-xl rounded-lg p-1.5 transition-all border',
                myEmoji === e
                  ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30'
                  : 'border-transparent hover:border-gray-200 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
              ]"
            >{{ e }}</button>
          </div>
        </div>

        <!-- Share -->
        <div class="relative" @mouseenter="onShareEnter" @mouseleave="onShareLeave">
          <button
            @click="copyInviteLink"
            title="Copy Invite Link"
            class="flex items-center gap-1.5 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
            </svg>
            <span class="hidden sm:inline whitespace-nowrap">Share Room</span>
          </button>
          <div
            v-if="showQR && qrDataUrl"
            class="absolute right-0 top-full mt-2 z-20 w-[160px] rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg p-2"
          >
            <img :src="qrDataUrl" alt="Room invite QR code" width="160" height="160" class="rounded" />
          </div>
        </div>

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
          <span class="hidden sm:inline">Timer</span>
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
          <span class="hidden sm:inline">Leave</span>
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
      <main class="flex-1 flex flex-col lg:flex-row">

        <!-- ── Note sidebar (left on desktop, top on mobile) ── -->
        <NoteSidebar :isOwner="isOwner" />

        <!-- ── Primary column ── -->
        <div class="flex-1 flex flex-col min-w-0">
          <div class="max-w-3xl w-full mx-auto px-4 pt-8 space-y-8">

            <!-- Round headline + current topic -->
            <div class="text-center space-y-1">
              <h2 class="text-3xl font-semibold text-gray-600 dark:text-gray-300">
                Round {{ roomStore.currentRound?.number }}
              </h2>
              <div v-if="roomStore.currentTopic">
                <a
                  v-if="roomStore.currentTopic.link"
                  :href="roomStore.currentTopic.link"
                  target="_blank"
                  rel="noopener"
                  class="inline-flex items-center gap-1.5 text-lg font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  <span class="font-mono">{{ roomStore.currentTopic.key }}</span><template v-if="roomStore.currentTopic.key">: </template>{{ roomStore.currentTopic.headline }}
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
                <span v-else class="text-lg font-medium text-gray-700 dark:text-gray-300">
                  <span class="font-mono">{{ roomStore.currentTopic.key }}</span><template v-if="roomStore.currentTopic.key">: </template>{{ roomStore.currentTopic.headline }}
                </span>
              </div>
            </div>

            <!-- Owner action (centered) -->
            <div v-if="isOwner" class="flex justify-center gap-3">
              <div
                class="relative"
                data-testid="thinking-music-wrapper"
                @mouseenter="onMusicWrapperEnter"
                @mouseleave="onMusicWrapperLeave"
              >
                <button
                  v-if="!roomStore.isRevealed"
                  @click="toggleThinkingMusic"
                  :disabled="allVoted && !thinkingActive"
                  :class="[
                    'rounded-lg px-8 py-2.5 font-semibold transition-colors',
                    thinkingActive
                      ? 'bg-amber-500 text-white hover:bg-amber-600'
                      : 'border border-amber-400 text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20',
                    allVoted && !thinkingActive ? 'opacity-50 cursor-not-allowed' : '',
                  ]"
                >
                  {{ thinkingActive ? '⏹ Stop Music' : '🎵 Thinking time…' }}
                </button>
                <div
                  v-if="thinkingActive && showVolume"
                  class="absolute left-0 right-0 -bottom-8 flex items-center gap-1 px-2"
                >
                  <span class="text-xs">🔈</span>
                  <input
                    type="range"
                    min="0" max="1" step="0.01"
                    v-model.number="volumeLevel"
                    class="w-full h-1 accent-amber-500 cursor-pointer"
                  />
                  <span class="text-xs">🔊</span>
                </div>
              </div>
              <button
                v-if="!roomStore.isRevealed"
                @click="reveal"
                :disabled="!allVoted"
                class="rounded-lg bg-green-600 px-8 py-2.5 font-semibold text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Reveal Cards
              </button>
              <template v-if="roomStore.isRevealed">
                <button
                  @click="newRound"
                  class="rounded-lg bg-indigo-600 px-8 py-2.5 font-semibold text-white hover:bg-indigo-700 transition-colors"
                >
                  Next Topic
                </button>
                <button
                  @click="retry"
                  class="rounded-lg border border-indigo-400 dark:border-indigo-500 px-8 py-2.5 font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                >
                  Revote
                </button>
              </template>
            </div>

            <!-- Participants -->
            <section>
              <h3 class="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wide">Participants</h3>
              <ul class="grid grid-cols-2 gap-2">
                <li
                  v-for="p in roomStore.participants"
                  :key="p.id"
                  :class="[
                    'flex items-center justify-between rounded-lg border bg-white dark:bg-gray-800 px-4 py-3 transition-opacity',
                    participantBorderClass(p),
                  ]"
                >
                  <span :class="['font-medium flex items-center gap-1.5', p.suspended ? 'text-gray-400 dark:text-gray-500' : '']">
                    <span v-if="p.emoji" class="text-lg leading-none">{{ p.emoji }}</span>
                    {{ p.nickname }}
                    <span v-if="p.is_owner" class="ml-1 text-xs text-indigo-500">owner</span>
                    <span v-if="p.suspended" class="ml-1 text-xs text-yellow-500 dark:text-yellow-400">suspended</span>
                  </span>
                  <span class="flex items-center gap-3">
                    <span :class="voteLabel(p).class">{{ voteLabel(p).text }}</span>
                    <span v-if="roomStore.isRevealed && voteExtremes.highest.has(p.id)"
                      class="text-xs font-semibold text-orange-500">▲</span>
                    <span v-if="roomStore.isRevealed && voteExtremes.lowest.has(p.id)"
                      class="text-xs font-semibold text-blue-500">▼</span>
                    <button
                      v-if="isOwner && !p.is_owner"
                      @click="suspend(p.id)"
                      :title="p.suspended ? 'Already suspended' : 'Suspend participant'"
                      :disabled="p.suspended"
                      class="text-gray-400 hover:text-yellow-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="6" y="4" width="4" height="16" rx="1"/>
                        <rect x="14" y="4" width="4" height="16" rx="1"/>
                      </svg>
                    </button>
                  </span>
                </li>
              </ul>
              <!-- Results after reveal -->
              <p v-if="roomStore.isRevealed && (numericAverage !== null || mostPopularVote !== null)" class="mt-3 text-sm text-gray-500 text-center space-x-4">
                <span v-if="numericAverage !== null">Average: <span class="font-bold text-gray-900 dark:text-gray-100">{{ numericAverage }}</span></span>
                <span v-if="mostPopularVote !== null">Most popular: <span class="font-bold text-gray-900 dark:text-gray-100">{{ mostPopularVote }}</span></span>
              </p>
            </section>

          </div>

          <!-- Card selection — full browser width on desktop -->
          <section v-if="!roomStore.isRevealed" class="w-full flex flex-col items-center gap-3 px-4 py-8 sm:py-6">
            <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Your vote</h3>
            <p v-if="isSuspended" class="text-sm text-yellow-600 dark:text-yellow-400">You are suspended — pick a card to re-enable yourself.</p>
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

          <div class="max-w-3xl w-full mx-auto px-4 pb-8">
            <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
          </div>
        </div>

        <!-- ── Topics sidebar (right on desktop, bottom on mobile) ── -->
        <TopicsSidebar :isOwner="isOwner" />

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
      <TimerDialog
        :open="timerDialog"
        :timerRemaining="timerRemaining"
        @start="startTimer"
        @stop="stopTimer"
        @close="timerDialog = false"
      />
    </template>
  </div>
</template>

<script setup>
// Main planning poker session page.
// Responsible for orchestrating room state, composables, voting, participant
// management, and the join overlay shown to share-link visitors.
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRoomStore } from '../stores/room'
import { useUserStore } from '../stores/user'
import { useThemeStore } from '../stores/theme'

import { useTimer } from '../composables/useTimer'
import { useThinkingMusic } from '../composables/useThinkingMusic'
import { useVoteAnalysis } from '../composables/useVoteAnalysis'
import { useShare } from '../composables/useShare'
import { useFireworks } from '../composables/useFireworks'
import { useJoinFlow } from '../composables/useJoinFlow'
import { useEmoji } from '../composables/useEmoji'

import NoteSidebar from '../components/NoteSidebar.vue'
import TopicsSidebar from '../components/TopicsSidebar.vue'
import TimerDialog from '../components/TimerDialog.vue'

const route = useRoute()
const router = useRouter()
const roomStore = useRoomStore()
const userStore = useUserStore()
const themeStore = useThemeStore()

const error = ref('')
const roomId = route.params.roomId
const timerDialog = ref(false)

// Shared authenticated fetch helper — injects the user's token into every request body.
async function apiFetch(path, method = 'POST', body = {}) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: userStore.token, ...body }),
  })
  if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText)
  return res.json()
}

// Derived participant state
const isOwner = computed(() => {
  const me = roomStore.room?.participants?.[userStore.participantId]
  return me?.is_owner ?? false
})

const isSuspended = computed(() => {
  const me = roomStore.room?.participants?.[userStore.participantId]
  return me?.suspended ?? false
})

const allVoted = computed(() => {
  const active = roomStore.participants.filter(p => !p.suspended)
  return active.length > 0 && active.every(p => p.vote)
})

// Composables
const { joining, joinNickname, joinError, joinRoom } =
  useJoinFlow(roomId, roomStore, userStore, router)

const { EMOJIS, myEmoji, moodOpen, moodAnchor, setEmoji } =
  useEmoji(roomId, userStore, apiFetch, error)

const { timerRemaining, formattedTimer, startCountdownFrom, startTimer, stopTimer } =
  useTimer(roomId, roomStore, userStore)

const { voteExtremes, numericAverage, mostPopularVote } =
  useVoteAnalysis(roomStore)

const { copyToast, showQR, qrDataUrl, onShareEnter, onShareLeave, copyInviteLink } =
  useShare()

const { thinkingActive, volumeLevel, showVolume, onMusicWrapperEnter, onMusicWrapperLeave,
        toggleThinkingMusic, startThinkingAudio, stopThinkingAudio } =
  useThinkingMusic(roomId, roomStore, userStore, isOwner, allVoted)

const { fireworksCanvas, fireworksActive } =
  useFireworks(roomStore)

// Locally tracked card selection; reset on new round or votes_reset so the
// UI reflects server state correctly after a reconnect.
const myVote = ref(null)

watch(() => roomStore.currentRound?.number, () => { myVote.value = null })
watch(() => roomStore.votesResetCount, () => { myVote.value = null })

async function vote(card) {
  error.value = ''
  // Optimistic toggle: apply locally first, roll back on API error.
  const newCard = myVote.value === card ? null : card
  myVote.value = newCard
  try {
    await apiFetch(`/api/rooms/${roomId}/vote`, 'POST', {
      participant_id: userStore.participantId,
      card: newCard,
    })
  } catch (e) {
    myVote.value = newCard === null ? card : null
    error.value = e.message
  }
}

async function reveal() {
  try { await apiFetch(`/api/rooms/${roomId}/reveal`) } catch (e) { error.value = e.message }
}

async function newRound() {
  try { await apiFetch(`/api/rooms/${roomId}/new-round`) } catch (e) { error.value = e.message }
}

async function retry() {
  try { await apiFetch(`/api/rooms/${roomId}/retry`) } catch (e) { error.value = e.message }
}

// Participant management
async function suspend(participantId) {
  try {
    await apiFetch(`/api/rooms/${roomId}/participants/${participantId}/suspend`, 'POST')
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

function participantBorderClass(p) {
  if (p.suspended) return 'opacity-50 border-gray-200 dark:border-gray-700'
  if (!roomStore.isRevealed && p.vote) return 'border-green-400 dark:border-green-500'
  if (voteExtremes.value.highest.has(p.id)) return 'border-orange-400 dark:border-orange-500'
  if (voteExtremes.value.lowest.has(p.id)) return 'border-blue-400 dark:border-blue-500'
  return 'border-gray-200 dark:border-gray-700'
}

function voteLabel(participant) {
  if (!roomStore.isRevealed) {
    if (participant.vote) return { text: '✓', class: 'text-green-500 font-bold text-[22px]' }
    return { text: '', class: '' }
  }
  return { text: participant.vote ?? '–', class: 'font-bold' }
}

onMounted(async () => {
  try {
    const res = await fetch(`/api/rooms/${roomId}`)
    if (!res.ok) { router.push({ name: 'home' }); return }
    const data = await res.json()
    roomStore.setRoom(data)
    const alreadyIn = userStore.participantId && data.participants?.[userStore.participantId]
    if (alreadyIn) {
      if (data.music_volume !== undefined) volumeLevel.value = data.music_volume
      roomStore.connectSSE(roomId)
      if (data.music_playing) startThinkingAudio()
      if (data.timer_ends_at) startCountdownFrom(data.timer_ends_at)
    } else {
      joining.value = true
    }
  } catch {
    router.push({ name: 'home' })
  }
})

onUnmounted(() => {
  roomStore.clear()
})
</script>
