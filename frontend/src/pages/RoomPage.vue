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
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707a1 1 0 00-1.414-1.414L9 11.172 7.707 9.879a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Mood
          </button>
          <!-- Dropdown -->
          <div
            v-if="moodOpen"
            class="absolute right-0 top-full mt-1.5 z-20 flex gap-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg px-2 py-1.5"
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
              {{ roomStore.currentTopic.short_name }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
              </svg>
            </a>
            <span v-else class="text-lg font-medium text-gray-700 dark:text-gray-300">
              {{ roomStore.currentTopic.short_name }}
            </span>
          </div>
        </div>

        <!-- Owner action (centered) -->
        <div v-if="isOwner" class="flex justify-center gap-3">
          <button
            v-if="!roomStore.isRevealed"
            @click="toggleThinkingMusic"
            :class="[
              'rounded-lg px-8 py-2.5 font-semibold transition-colors',
              thinkingActive
                ? 'bg-amber-500 text-white hover:bg-amber-600'
                : 'border border-amber-400 text-amber-600 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20',
            ]"
          >
            {{ thinkingActive ? '⏹ Stop Music' : '🎵 Thinking time…' }}
          </button>
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
                'flex items-center justify-between rounded-lg border bg-white dark:bg-gray-800 px-4 py-3',
                !roomStore.isRevealed && p.vote
                  ? 'border-green-400 dark:border-green-500'
                  : 'border-gray-200 dark:border-gray-700'
              ]"
            >
              <span class="font-medium flex items-center gap-1.5">
                <span v-if="p.emoji" class="text-lg leading-none">{{ p.emoji }}</span>
                {{ p.nickname }}
                <span v-if="p.is_owner" class="ml-1 text-xs text-indigo-500">owner</span>
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

        <!-- Topics -->
        <section v-if="roomStore.topics.length > 0 || isOwner">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Topics</h3>
            <button
              v-if="isOwner"
              @click="showAddTopic = !showAddTopic"
              class="flex items-center gap-1 text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
              </svg>
              Add Topic
            </button>
          </div>

          <!-- Add topic form -->
          <div v-if="showAddTopic" class="mb-3 flex gap-2">
            <input
              v-model="newTopicName"
              placeholder="Short name"
              @keydown.enter="addTopic"
              class="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              v-model="newTopicLink"
              placeholder="Link (optional)"
              @keydown.enter="addTopic"
              class="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              @click="addTopic"
              :disabled="!newTopicName.trim()"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >Add</button>
            <button
              @click="showAddTopic = false"
              class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >Cancel</button>
          </div>

          <!-- Topic list -->
          <ol class="space-y-2">
            <li
              v-for="(topic, idx) in roomStore.topics"
              :key="topic.id"
              :class="[
                'flex items-center gap-3 rounded-lg border px-4 py-2.5 bg-white dark:bg-gray-800 transition-colors',
                idx === roomStore.currentTopicIndex
                  ? 'border-indigo-400 dark:border-indigo-500'
                  : 'border-gray-200 dark:border-gray-700'
              ]"
            >
              <span class="w-5 text-xs text-gray-400 shrink-0">{{ idx + 1 }}</span>
              <span
                v-if="idx === roomStore.currentTopicIndex"
                class="h-2 w-2 rounded-full bg-indigo-500 shrink-0"
              ></span>
              <a
                v-if="topic.link"
                :href="topic.link"
                target="_blank"
                rel="noopener"
                class="flex-1 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline truncate"
              >{{ topic.short_name }}</a>
              <span v-else class="flex-1 text-sm font-medium truncate">{{ topic.short_name }}</span>
              <!-- Estimated badge -->
              <span v-if="topic.estimates != null" class="flex items-center gap-1 shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span
                  v-for="e in topic.estimates"
                  :key="e"
                  class="rounded-full bg-green-100 dark:bg-green-900/40 px-1.5 py-0.5 text-xs font-medium text-green-700 dark:text-green-300"
                >{{ e }}</span>
              </span>
              <div v-if="isOwner" class="flex items-center gap-1 shrink-0">
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
                  @click="moveTopic(idx, -1)"
                  :disabled="idx === 0"
                  class="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 disabled:opacity-30 transition-colors"
                  title="Move up"
                >↑</button>
                <button
                  @click="moveTopic(idx, 1)"
                  :disabled="idx === roomStore.topics.length - 1"
                  class="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 disabled:opacity-30 transition-colors"
                  title="Move down"
                >↓</button>
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
        </section>

        <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
      </main>

      <!-- Edit topic dialog -->
      <div
        v-if="editingTopic"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="editingTopic = null"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-96 space-y-4">
          <h3 class="text-lg font-semibold">Edit Topic</h3>
          <div class="space-y-3">
            <input
              v-model="editTopicName"
              placeholder="Short name"
              @keydown.enter="saveEditTopic"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              v-model="editTopicLink"
              placeholder="Link (optional)"
              @keydown.enter="saveEditTopic"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div class="flex justify-end gap-3">
            <button
              @click="editingTopic = null"
              class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >Cancel</button>
            <button
              @click="saveEditTopic"
              :disabled="!editTopicName.trim()"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >Save</button>
          </div>
        </div>
      </div>

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

// Join flow for share-link visitors
const joining = ref(false)
const joinNickname = ref(userStore.nickname ?? '')
const joinError = ref('')

async function joinRoom() {
  if (!joinNickname.value.trim()) return
  joinError.value = ''
  try {
    const res = await fetch(`/api/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname: joinNickname.value.trim() }),
    })
    if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText)
    const data = await res.json()
    userStore.setNickname(joinNickname.value.trim())
    userStore.setSession(data.participant_id, data.token)
    const refreshed = await fetch(`/api/rooms/${roomId}`)
    if (refreshed.ok) roomStore.setRoom(await refreshed.json())
    joining.value = false
    roomStore.connectSSE(roomId)
  } catch (e) {
    joinError.value = e.message
  }
}

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

const EMOJIS = ['🤔', '😄', '😢', '❤️', '☕', '🍺']
const myEmoji = ref(null)
const moodOpen = ref(false)
const moodAnchor = ref(null)

const thinkingActive = computed(() => roomStore.room?.music_playing ?? false)
let thinkingAudio = null

function startThinkingAudio() {
  if (thinkingAudio) return
  thinkingAudio = new Audio('/sounds/thinking-time.mp3')
  thinkingAudio.loop = true
  thinkingAudio.play()
}

function stopThinkingAudio() {
  thinkingAudio?.pause()
  thinkingAudio = null
}

async function toggleThinkingMusic() {
  try {
    await apiFetch(`/api/rooms/${roomId}/music`, 'POST', { playing: !thinkingActive.value })
  } catch (e) { error.value = e.message }
}

watch(thinkingActive, (playing) => {
  if (playing) startThinkingAudio()
  else stopThinkingAudio()
})


function onClickOutsideMood(e) {
  if (moodAnchor.value && !moodAnchor.value.contains(e.target)) {
    moodOpen.value = false
  }
}

async function setEmoji(emoji) {
  const next = myEmoji.value === emoji ? null : emoji
  myEmoji.value = next
  try {
    await apiFetch(`/api/rooms/${roomId}/emoji`, 'POST', {
      participant_id: userStore.participantId,
      emoji: next,
    })
  } catch (e) {
    myEmoji.value = myEmoji.value === null ? emoji : null // revert
    error.value = e.message
  }
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

watch(allVoted, (voted) => {
  if (voted && thinkingActive.value && isOwner.value) {
    apiFetch(`/api/rooms/${roomId}/music`, 'POST', { playing: false }).catch(() => {})
  }
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

async function retry() {
  try { await apiFetch(`/api/rooms/${roomId}/retry`) } catch (e) { error.value = e.message }
}

// Topics
const showAddTopic = ref(false)
const newTopicName = ref('')
const newTopicLink = ref('')

async function addTopic() {
  if (!newTopicName.value.trim()) return
  try {
    await apiFetch(`/api/rooms/${roomId}/topics`, 'POST', {
      short_name: newTopicName.value.trim(),
      link: newTopicLink.value.trim(),
    })
    newTopicName.value = ''
    newTopicLink.value = ''
    showAddTopic.value = false
  } catch (e) { error.value = e.message }
}

async function moveTopic(idx, dir) {
  const topics = [...roomStore.topics]
  const newIdx = idx + dir
  if (newIdx < 0 || newIdx >= topics.length) return
  ;[topics[idx], topics[newIdx]] = [topics[newIdx], topics[idx]]
  try {
    await apiFetch(`/api/rooms/${roomId}/topics`, 'PUT', {
      topic_ids: topics.map(t => t.id),
    })
  } catch (e) { error.value = e.message }
}

async function deleteTopic(topicId) {
  try {
    await apiFetch(`/api/rooms/${roomId}/topics/${topicId}`, 'DELETE')
  } catch (e) { error.value = e.message }
}

const editingTopic = ref(null)
const editTopicName = ref('')
const editTopicLink = ref('')

function openEditTopic(topic) {
  editingTopic.value = topic
  editTopicName.value = topic.short_name
  editTopicLink.value = topic.link
}

async function saveEditTopic() {
  if (!editTopicName.value.trim() || !editingTopic.value) return
  try {
    await apiFetch(`/api/rooms/${roomId}/topics/${editingTopic.value.id}`, 'PATCH', {
      short_name: editTopicName.value.trim(),
      link: editTopicLink.value.trim(),
    })
    editingTopic.value = null
  } catch (e) { error.value = e.message }
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
  document.addEventListener('click', onClickOutsideMood, true)
  try {
    const res = await fetch(`/api/rooms/${roomId}`)
    if (!res.ok) { router.push({ name: 'home' }); return }
    const data = await res.json()
    roomStore.setRoom(data)
    const alreadyIn = userStore.participantId && data.participants?.[userStore.participantId]
    if (alreadyIn) {
      roomStore.connectSSE(roomId)
      if (data.music_playing) startThinkingAudio()
    } else {
      joining.value = true
    }
  } catch {
    router.push({ name: 'home' })
  }
})

onBeforeUnmount(() => {
  clearInterval(timerInterval)
  cancelAnimationFrame(fireworksRaf)
  clearTimeout(copyToastTimer)
  document.removeEventListener('click', onClickOutsideMood, true)
  stopThinkingAudio()
})

onUnmounted(() => {
  roomStore.clear()
})
</script>
