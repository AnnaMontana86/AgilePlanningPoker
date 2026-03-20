<template>
  <main class="flex min-h-screen items-center justify-center p-4">
    <div class="w-full max-w-md space-y-6">
      <div class="text-center space-y-1">
        <p class="text-xs font-semibold tracking-widest text-indigo-500 uppercase">Agile Estimation</p>
        <h1 class="text-4xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-500 bg-clip-text text-transparent">
          Planning Poker
        </h1>
      </div>

      <!-- Nickname -->
      <section class="space-y-2">
        <label class="block text-sm font-medium" for="nickname">Your nickname</label>
        <input
          id="nickname"
          v-model="nickname"
          @input="nicknameError = ''"
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
        <p v-if="nicknameError" class="text-red-500 text-sm">{{ nicknameError }}</p>
      </section>

      <!-- Action Buttons -->
      <div class="flex gap-4">
        <button
          @click="openCreate"
          class="flex-1 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Create a room
        </button>
        <button
          @click="openJoin"
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

      <!-- Legal footer -->
      <div class="pt-2 text-center text-xs text-gray-400 dark:text-gray-500 space-x-2">
        <button @click="openLegal('impressum')" class="hover:underline hover:text-gray-600 dark:hover:text-gray-300 transition-colors">Legal Notice</button>
        <span aria-hidden="true">·</span>
        <button @click="openLegal('privacy')" class="hover:underline hover:text-gray-600 dark:hover:text-gray-300 transition-colors">Privacy</button>
        <span aria-hidden="true">·</span>
        <button @click="openLegal('disclaimer')" class="hover:underline hover:text-gray-600 dark:hover:text-gray-300 transition-colors">Disclaimer</button>
      </div>
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
          <div class="space-y-1">
            <input
              v-model="newRoomName"
              @input="roomNameError = ''"
              type="text"
              maxlength="80"
              placeholder="Room name"
              :class="[
                'w-full rounded-lg border bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 transition-colors',
                roomNameError ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 dark:border-gray-600 focus:ring-indigo-500',
              ]"
            />
            <p v-if="roomNameError" class="text-red-500 text-xs">{{ roomNameError }}</p>
          </div>
          <select
            v-model="selectedCardSet"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select a card set</option>
            <option v-for="(cards, name) in cardSets" :key="name" :value="name">
              {{ name }} ({{ cards.slice(0, 5).join(', ') }}{{ cards.length > 5 ? ', …' : '' }})
            </option>
            <option value="__custom__">Custom…</option>
          </select>
          <div v-if="selectedCardSet === '__custom__'" class="space-y-1">
            <input
              v-model="customCardInput"
              @input="customCardError = ''"
              type="text"
              placeholder="e.g. 1, 2, 3, 5, 8, 13, ?"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            />
            <p v-if="customCardError" class="text-red-500 text-xs">{{ customCardError }}</p>
            <p v-else-if="parsedCustomCards.length" class="text-gray-500 dark:text-gray-400 text-xs">
              {{ parsedCustomCards.length }} card{{ parsedCustomCards.length !== 1 ? 's' : '' }}:
              {{ parsedCustomCards.join(', ') }}
            </p>
            <p v-else class="text-gray-400 dark:text-gray-500 text-xs">Enter comma-separated values (2–20)</p>
          </div>
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

    <!-- Legal Modal -->
    <Teleport to="body">
      <div
        v-if="legalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="legalOpen = false"
      >
        <div class="w-full max-w-lg rounded-2xl bg-white dark:bg-gray-900 shadow-xl flex flex-col max-h-[80vh]">
          <!-- Header with tabs -->
          <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 px-6 pt-5 pb-0 shrink-0">
            <nav class="flex gap-1 -mb-px">
              <button
                v-for="tab in legalTabs"
                :key="tab.key"
                @click="legalSection = tab.key"
                :class="[
                  'px-3 py-2 text-sm font-medium border-b-2 transition-colors',
                  legalSection === tab.key
                    ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300',
                ]"
              >{{ tab.label }}</button>
            </nav>
            <button @click="legalOpen = false" class="mb-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="overflow-y-auto px-6 py-5 text-sm text-gray-700 dark:text-gray-300 space-y-4 leading-relaxed">

            <!-- Legal Notice / Impressum -->
            <template v-if="legalSection === 'impressum'">
              <p class="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide font-semibold">Impressum · Legal Notice pursuant to § 5 TMG</p>
              <p>
                This web application is operated as a free, non-commercial, open-source project
                under the <strong>MIT License</strong>. The source code is publicly available on GitHub.
              </p>
              <div>
                <p class="font-semibold">Responsible operator</p>
                <p class="text-gray-500 dark:text-gray-400 italic">
                  [Name of operator or organisation]<br>
                  [Street, House number]<br>
                  [Postcode, City, Country]<br>
                  E-mail: [contact@example.com]
                </p>
                <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
                  (Please replace the placeholders above with the actual operator's details
                  before deploying publicly. German law requires a complete Impressum for
                  publicly accessible web services — §§ 5–6 TMG, § 18 MStV.)
                </p>
              </div>
              <div>
                <p class="font-semibold">Responsible for editorial content (§ 18 Abs. 2 MStV)</p>
                <p class="text-gray-500 dark:text-gray-400 italic">[Same as above]</p>
              </div>
              <div>
                <p class="font-semibold">EU Online Dispute Resolution</p>
                <p>
                  The European Commission provides a platform for online dispute resolution (ODR):
                  <span class="font-mono text-xs">https://ec.europa.eu/consumers/odr</span>.
                  We are neither obliged nor willing to participate in dispute resolution proceedings
                  before a consumer arbitration board, as this is a non-commercial service.
                </p>
              </div>
            </template>

            <!-- Privacy Notice -->
            <template v-if="legalSection === 'privacy'">
              <p class="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide font-semibold">Privacy Notice · Datenschutzerklärung (GDPR / DSGVO)</p>
              <div>
                <p class="font-semibold">1. Controller</p>
                <p>The operator listed in the Legal Notice is the data controller within the meaning of Art. 4 (7) GDPR.</p>
              </div>
              <div>
                <p class="font-semibold">2. What data we process</p>
                <p>This application is designed to minimise data collection:</p>
                <ul class="list-disc list-inside space-y-1 mt-1">
                  <li>
                    <strong>Nicknames</strong> — entered voluntarily by you. Stored in server memory
                    only for the duration of the active room session. Rooms expire automatically
                    (typically after a few hours of inactivity) and all associated data is then
                    permanently deleted from memory. Nothing is written to a database or persistent disk storage.
                  </li>
                  <li>
                    <strong>Session tokens</strong> — a randomly generated identifier is stored in
                    your browser's <code>localStorage</code> so you can reconnect to your room after
                    a page refresh. It is never transmitted to any third party and is cleared when
                    you leave the room or close the application.
                  </li>
                  <li>
                    <strong>Server access logs</strong> — your IP address, request timestamp, and
                    HTTP request URL are automatically recorded in standard web-server logs as required
                    for the secure operation of any internet service (legal basis: Art. 6 (1)(f) GDPR —
                    legitimate interest in IT security). Log files are not shared and are deleted
                    according to the operator's log-retention policy.
                  </li>
                </ul>
              </div>
              <div>
                <p class="font-semibold">3. No cookies, no tracking</p>
                <p>
                  We do not set cookies. We do not use analytics tools, advertising networks,
                  or any third-party tracking services.
                </p>
              </div>
              <div>
                <p class="font-semibold">4. Data transfers</p>
                <p>
                  No personal data is transferred to third parties or to countries outside the
                  European Economic Area (EEA).
                </p>
              </div>
              <div>
                <p class="font-semibold">5. Your rights (Art. 15–22 GDPR)</p>
                <p>
                  You have the right to access, rectify, erase, restrict, or object to the
                  processing of your personal data, and the right to data portability.
                  Because nicknames and session tokens are held only in volatile memory and
                  are not linked to a verified identity, most requests can be fulfilled
                  immediately by leaving the room (which clears all in-memory data).
                  For inquiries regarding server logs, please contact the operator listed
                  in the Legal Notice.
                </p>
              </div>
              <div>
                <p class="font-semibold">6. Right to lodge a complaint</p>
                <p>
                  You have the right to lodge a complaint with a supervisory authority.
                  In Germany, the competent authority is the data protection authority
                  (Datenschutzbehörde) of the federal state in which the operator is located.
                </p>
              </div>
            </template>

            <!-- Disclaimer -->
            <template v-if="legalSection === 'disclaimer'">
              <p class="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide font-semibold">Disclaimer · Haftungsausschluss</p>
              <div>
                <p class="font-semibold">No warranty</p>
                <p>
                  This software is provided <strong>"as is"</strong>, without warranty of any kind,
                  express or implied, including but not limited to the warranties of merchantability,
                  fitness for a particular purpose, and non-infringement. In no event shall the
                  authors or copyright holders be liable for any claim, damages, or other liability,
                  whether in an action of contract, tort, or otherwise, arising from, out of, or in
                  connection with the software or the use or other dealings in the software
                  (MIT License, full text available in the source repository).
                </p>
              </div>
              <div>
                <p class="font-semibold">Service availability</p>
                <p>
                  The operator makes no guarantee of uninterrupted availability of this service.
                  The service may be taken offline or modified at any time without prior notice.
                  No data entered in the application should be considered permanently stored.
                </p>
              </div>
              <div>
                <p class="font-semibold">External links</p>
                <p>
                  Topic links entered by users point to external websites. The operator has no
                  control over the content of those sites and accepts no liability for them.
                </p>
              </div>
              <div>
                <p class="font-semibold">Haftung für Inhalte (§ 7 Abs. 1 TMG)</p>
                <p>
                  Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen
                  Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir
                  als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde
                  Informationen zu überwachen. Haftungsansprüche, die sich auf Schäden materieller
                  oder ideeller Art beziehen, welche durch die Nutzung dieser Software verursacht
                  wurden, sind ausgeschlossen, sofern kein nachweislich vorsätzliches oder grob
                  fahrlässiges Verschulden vorliegt.
                </p>
              </div>
            </template>

          </div>
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const nickname = ref(userStore.nickname)
const newRoomName = ref('')
const selectedCardSet = ref('')
const customCardInput = ref('')
const customCardError = ref('')
const joinCode = ref('')
const cardSets = ref({})
const error = ref('')
const showCreate = ref(false)
const showJoin = ref(false)
const nicknameError = ref('')
const roomNameError = ref('')

const legalOpen = ref(false)
const legalSection = ref('impressum')
const legalTabs = [
  { key: 'impressum', label: 'Legal Notice' },
  { key: 'privacy',   label: 'Privacy' },
  { key: 'disclaimer', label: 'Disclaimer' },
]
function openLegal(section) {
  legalSection.value = section
  legalOpen.value = true
}

const parsedCustomCards = computed(() =>
  customCardInput.value
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)
)

const canCreate = computed(() => {
  if (!nickname.value.trim() || !newRoomName.value.trim() || !selectedCardSet.value) return false
  if (selectedCardSet.value === '__custom__') {
    return parsedCustomCards.value.length >= 2 && parsedCustomCards.value.length <= 20
  }
  return true
})
const canJoin = computed(() => nickname.value.trim() && joinCode.value.trim())

function validateNickname() {
  if (!nickname.value.trim()) { nicknameError.value = 'Please enter a nickname first.'; return false }
  if (nickname.value.includes(';')) { nicknameError.value = 'Nickname must not contain ";".'; return false }
  return true
}

function openCreate() {
  if (validateNickname()) showCreate.value = true
}

function openJoin() {
  if (validateNickname()) showJoin.value = true
}

watch(showCreate, open => {
  if (!open) {
    newRoomName.value = ''
    roomNameError.value = ''
    selectedCardSet.value = ''
    customCardInput.value = ''
    customCardError.value = ''
  }
})

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
  customCardError.value = ''

  if (newRoomName.value.includes(';')) {
    roomNameError.value = 'Room name must not contain ";".'
    return
  }

  if (selectedCardSet.value === '__custom__') {
    if (parsedCustomCards.value.length < 2) {
      customCardError.value = 'Enter at least 2 values.'
      return
    }
    if (parsedCustomCards.value.length > 20) {
      customCardError.value = 'Maximum 20 values allowed.'
      return
    }
  }

  userStore.setNickname(nickname.value.trim())
  const body = selectedCardSet.value === '__custom__'
    ? { name: newRoomName.value.trim(), custom_card_set: { name: 'Custom', cards: parsedCustomCards.value }, owner_nickname: userStore.nickname }
    : { name: newRoomName.value.trim(), card_set_name: selectedCardSet.value, owner_nickname: userStore.nickname }

  try {
    const res = await fetch('/api/rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
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
