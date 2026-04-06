<template>
  <main class="hp-root">
    <!-- Atmospheric dot-grid -->
    <div class="hp-grid-bg" aria-hidden="true" />

    <div class="hp-layout">

      <!-- ── FORM SIDE ── -->
      <div class="hp-form-side">
        <div class="hp-form-content">

          <!-- Brand header -->
          <header class="hp-header hp-rise" style="--hp-d:0s">
            <div class="hp-badge">
              <span class="hp-badge-pip" />
              Agile Estimation
            </div>
            <h1 class="hp-headline">Planning<br><em>Poker</em></h1>
            <p class="hp-tagline">Align your team. Ship with confidence.</p>
          </header>

          <!-- Nickname -->
          <div class="hp-field hp-rise" style="--hp-d:0.08s">
            <label class="hp-label" for="nickname">Your nickname</label>
            <input
              id="nickname"
              v-model="nickname"
              @input="nicknameError = ''"
              type="text"
              maxlength="32"
              placeholder="Enter your nickname"
              :class="['hp-input', { 'hp-input--error': nicknameError }]"
            />
            <p v-if="nicknameError" class="hp-error-msg">{{ nicknameError }}</p>
          </div>

          <!-- CTAs -->
          <div class="hp-ctas hp-rise" style="--hp-d:0.16s">
            <button @click="openCreate" class="hp-btn hp-btn--primary">
              <svg xmlns="http://www.w3.org/2000/svg" class="hp-btn-ico" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd"/>
              </svg>
              Create a room
            </button>
            <button @click="openJoin" class="hp-btn hp-btn--ghost">
              <svg xmlns="http://www.w3.org/2000/svg" class="hp-btn-ico" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V7.414A1 1 0 0015.707 7l-4-4A1 1 0 0011 2.586V2H4a1 1 0 00-1 1zm9 1.414L14.586 7H12V4.414zM4 4h7v4a1 1 0 001 1h4v8H4V4z" clip-rule="evenodd"/>
                <path d="M7 9a1 1 0 000 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7a1 1 0 10-2 0v2H7z"/>
              </svg>
              Join a room
            </button>
          </div>

          <p v-if="error" class="hp-error-msg hp-error-msg--center">{{ error }}</p>

        </div>
      </div>

      <!-- ── VISUAL SIDE ── -->
      <div class="hp-visual" aria-hidden="true">
        <div class="hp-card-fan">
          <!-- 3♣ -->
          <div class="hp-card" style="--cr:-22deg;--ctx:-90px;--cty:35px;--cd:0.1s">
            <span class="hp-c-corner">3<br>♣</span>
            <span class="hp-c-big">3</span>
            <span class="hp-c-suit">♣</span>
            <span class="hp-c-corner hp-c-corner--br">3<br>♣</span>
          </div>
          <!-- 5♦ -->
          <div class="hp-card" style="--cr:-9deg;--ctx:-32px;--cty:6px;--cd:0.2s">
            <span class="hp-c-corner hp-c-red">5<br>♦</span>
            <span class="hp-c-big">5</span>
            <span class="hp-c-suit hp-c-red">♦</span>
            <span class="hp-c-corner hp-c-corner--br hp-c-red">5<br>♦</span>
          </div>
          <!-- 8♥ -->
          <div class="hp-card" style="--cr:5deg;--ctx:28px;--cty:-6px;--cd:0.3s">
            <span class="hp-c-corner hp-c-red">8<br>♥</span>
            <span class="hp-c-big">8</span>
            <span class="hp-c-suit hp-c-red">♥</span>
            <span class="hp-c-corner hp-c-corner--br hp-c-red">8<br>♥</span>
          </div>
          <!-- 13♠ — accent top card -->
          <div class="hp-card hp-card--top" style="--cr:17deg;--ctx:80px;--cty:20px;--cd:0.4s">
            <span class="hp-c-corner">13<br>♠</span>
            <span class="hp-c-big hp-c-big--sm">13</span>
            <span class="hp-c-suit">♠</span>
            <span class="hp-c-corner hp-c-corner--br">13<br>♠</span>
          </div>
        </div>
        <p class="hp-visual-label">Vote · Reveal · Align</p>
      </div>

    </div><!-- /hp-layout -->

    <!-- ── Page footer ── -->
    <footer class="hp-page-footer hp-rise" style="--hp-d:0.24s">
      <button @click="openLegal('impressum')" class="hp-legal-link">Legal Notice</button>
      <span aria-hidden="true">·</span>
      <button @click="openLegal('privacy')" class="hp-legal-link">Privacy</button>
      <span aria-hidden="true">·</span>
      <button @click="openLegal('disclaimer')" class="hp-legal-link">Disclaimer</button>
    </footer>

    <!-- ── Create Room Dialog ── -->
    <Teleport to="body">
      <div
        v-if="showCreate"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showCreate = false"
      >
        <div class="w-full max-w-sm rounded-2xl bg-[var(--hp-surface)] shadow-xl p-6 space-y-4" style="color: var(--hp-text)">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Create a room</h2>
            <button @click="showCreate = false" class="text-[var(--hp-muted)] hover:text-[var(--hp-text)] transition-colors">
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
                'w-full rounded-lg border bg-[var(--hp-surface)] px-4 py-2 focus:outline-none focus:ring-2 transition-colors',
                roomNameError ? 'border-red-500 focus:ring-red-500' : 'border-[var(--hp-border)] focus:ring-[var(--hp-accent)]',
              ]"
              :style="{ color: 'var(--hp-text)' }"
            />
            <p v-if="roomNameError" class="text-red-500 text-xs">{{ roomNameError }}</p>
          </div>
          <select
            v-model="selectedCardSet"
            class="w-full rounded-lg border border-[var(--hp-border)] bg-[var(--hp-surface)] px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--hp-accent)]"
            :style="{ color: 'var(--hp-text)' }"
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
              class="w-full rounded-lg border border-[var(--hp-border)] bg-[var(--hp-surface)] px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--hp-accent)] text-sm"
              :style="{ color: 'var(--hp-text)' }"
            />
            <p v-if="customCardError" class="text-red-500 text-xs">{{ customCardError }}</p>
            <p v-else-if="parsedCustomCards.length" class="text-[var(--hp-muted)] text-xs">
              {{ parsedCustomCards.length }} card{{ parsedCustomCards.length !== 1 ? 's' : '' }}:
              {{ parsedCustomCards.join(', ') }}
            </p>
            <p v-else class="text-[var(--hp-muted)] text-xs">Enter comma-separated values (2–20)</p>
          </div>
          <button
            :disabled="!canCreate"
            @click="createRoom"
            class="w-full rounded-lg bg-[var(--hp-accent)] px-4 py-2 font-semibold text-white hover:bg-[var(--hp-accent-h)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Create Room
          </button>
        </div>
      </div>
    </Teleport>

    <!-- ── Legal Modal ── -->
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

    <!-- ── Join Room Dialog ── -->
    <Teleport to="body">
      <div
        v-if="showJoin"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
        @click.self="showJoin = false"
      >
        <div class="w-full max-w-sm rounded-2xl bg-[var(--hp-surface)] shadow-xl p-6 space-y-4" style="color: var(--hp-text)">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold">Join a room</h2>
            <button @click="showJoin = false" class="text-[var(--hp-muted)] hover:text-[var(--hp-text)] transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          <input
            v-model="joinCode"
            type="text"
            placeholder="Room ID or paste invite link"
            class="w-full rounded-lg border border-[var(--hp-border)] bg-[var(--hp-surface)] px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--hp-accent)]"
            :style="{ color: 'var(--hp-text)' }"
          />
          <button
            :disabled="!canJoin"
            @click="joinRoom"
            class="w-full rounded-lg border border-[var(--hp-accent)] px-4 py-2 font-semibold text-[var(--hp-accent)] hover:bg-[var(--hp-accent)]/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Join Room
          </button>
        </div>
      </div>
    </Teleport>
  </main>
</template>

<script setup>
// Landing page for creating and joining rooms.
// Responsible for the nickname form, create/join dialogs, card-set
// selection (including custom sets), and the legal information modal.
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

<style scoped>
/* ─── Design tokens (light) ─── */
.hp-root {
  --accent:      #C96B30;
  --accent-h:    #A85424;
  --surface:     #FFFFFF;
  --border:      #DDD9CF;
  --text:        #1C1A17;
  --muted:       #8A8276;
  --bg:          #F5F3EF;
  --card-sh:     0 8px 28px rgba(0,0,0,.09), 0 2px 8px rgba(0,0,0,.06);
  --card-sh-lg:  0 20px 56px rgba(0,0,0,.13), 0 6px 18px rgba(0,0,0,.08);
  --ease-out:    cubic-bezier(.16,1,.3,1);
}
/* ─── Dark mode overrides ─── */
:global(.dark) .hp-root {
  --accent:      #E88050;
  --accent-h:    #F09060;
  --surface:     #1E1C19;
  --border:      #2D2A26;
  --text:        #EDE9E3;
  --muted:       #7A7570;
  --bg:          #111009;
  --card-sh:     0 8px 28px rgba(0,0,0,.4),  0 2px 8px rgba(0,0,0,.25);
  --card-sh-lg:  0 20px 56px rgba(0,0,0,.6), 0 6px 18px rgba(0,0,0,.4);
}

/* ─── Root shell ─── */
.hp-root {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', system-ui, sans-serif;
  overflow: hidden;
}

/* ─── Dot-grid atmosphere ─── */
.hp-grid-bg {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, var(--border) 1.5px, transparent 1.5px);
  background-size: 28px 28px;
  opacity: .6;
  pointer-events: none;
}

/* ─── Page grid ─── */
.hp-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  flex: 1;
  position: relative;
  z-index: 1;
}
@media (max-width: 768px) {
  .hp-layout               { grid-template-columns: 1fr; }
  .hp-visual               { display: none; }
  .hp-form-side            { justify-content: center; padding: 3rem 1.5rem; }
}

/* ─── Form column ─── */
.hp-form-side {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 4rem 3.5rem 4rem 2rem;
}
.hp-form-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 420px;
}

/* ─── Brand header ─── */
.hp-header { display: flex; flex-direction: column; gap: .65rem; }

.hp-badge {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: .68rem;
  font-weight: 500;
  letter-spacing: .09em;
  text-transform: uppercase;
  color: var(--muted);
  padding: .28rem .75rem .28rem .5rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  width: fit-content;
  background: var(--surface);
}
.hp-badge-pip {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
  animation: hp-pulse 2.4s ease-in-out infinite;
}
@keyframes hp-pulse {
  0%, 100% { box-shadow: 0 0 0 0   rgba(34,197,94,.5); }
  55%       { box-shadow: 0 0 0 5px rgba(34,197,94,0);  }
}

.hp-headline {
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  font-size: clamp(2.8rem, 4.5vw, 4.25rem);
  font-weight: 800;
  line-height: 1.0;
  letter-spacing: -.035em;
  color: var(--text);
  margin: 0;
}
.hp-headline em {
  font-style: italic;
  color: var(--accent);
}

.hp-tagline {
  font-size: .95rem;
  color: var(--muted);
  line-height: 1.55;
  font-weight: 400;
  margin: 0;
}

/* ─── Nickname field ─── */
.hp-field { display: flex; flex-direction: column; gap: .4rem; }

.hp-label {
  font-size: .72rem;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: .07em;
  text-transform: uppercase;
}

.hp-input {
  width: 100%;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  color: var(--text);
  padding: .75rem 1rem;
  font-size: 1rem;
  font-family: inherit;
  outline: none;
  transition: border-color .15s ease, box-shadow .15s ease;
  box-sizing: border-box;
}
.hp-input::placeholder { color: var(--muted); opacity: .65; }
.hp-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(201,107,48,.18);
}
:global(.dark) .hp-input:focus {
  box-shadow: 0 0 0 3px rgba(232,128,80,.18);
}
.hp-input--error              { border-color: #ef4444; }
.hp-input--error:focus        { box-shadow: 0 0 0 3px rgba(239,68,68,.18); }

.hp-error-msg               { font-size: .82rem; color: #ef4444; }
.hp-error-msg--center       { text-align: center; }

/* ─── CTA buttons ─── */
.hp-ctas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .75rem;
}
.hp-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .45rem;
  padding: .8rem 1.2rem;
  border-radius: 10px;
  font-size: .92rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background .15s ease, border-color .15s ease,
              color .15s ease, transform .1s ease, box-shadow .15s ease;
  white-space: nowrap;
  border: 1.5px solid transparent;
}
.hp-btn:active { transform: scale(.97); }
.hp-btn-ico    { width: 17px; height: 17px; flex-shrink: 0; }

.hp-btn--primary {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  box-shadow: 0 4px 16px rgba(201,107,48,.3);
}
.hp-btn--primary:hover {
  background: var(--accent-h);
  border-color: var(--accent-h);
  box-shadow: 0 6px 22px rgba(201,107,48,.4);
}
:global(.dark) .hp-btn--primary {
  box-shadow: 0 4px 16px rgba(232,128,80,.25);
}
:global(.dark) .hp-btn--primary:hover {
  box-shadow: 0 6px 22px rgba(232,128,80,.35);
}

.hp-btn--ghost {
  background: transparent;
  color: var(--accent);
  border-color: var(--accent);
}
.hp-btn--ghost:hover {
  background: rgba(201,107,48,.08);
}
:global(.dark) .hp-btn--ghost:hover {
  background: rgba(232,128,80,.1);
}

/* ─── Page footer (centered, full-width) ─── */
.hp-page-footer {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .5rem;
  padding: 1rem 1.5rem 1.5rem;
  color: var(--muted);
  font-size: .75rem;
}

.hp-legal-link {
  background: none;
  border: none;
  color: inherit;
  font-size: inherit;
  font-family: inherit;
  cursor: pointer;
  padding: 0;
  transition: color .15s ease;
}
.hp-legal-link:hover { color: var(--text); text-decoration: underline; }

/* ─── Visual column ─── */
.hp-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem 4rem 3.5rem;
  gap: 2.5rem;
}

/* ─── Card fan ─── */
.hp-card-fan {
  position: relative;
  width: 320px;
  height: 290px;
}

.hp-card {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 128px;
  height: 188px;
  margin: -94px 0 0 -64px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--card-sh-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .1rem;
  padding: .6rem;

  translate: var(--ctx, 0px) var(--cty, 0px);
  rotate: var(--cr, 0deg);

  animation: hp-card-in .75s var(--ease-out) both;
  animation-delay: var(--cd, 0s);
}
.hp-card--top {
  background: var(--accent);
  border-color: transparent;
}
.hp-card--top .hp-c-corner,
.hp-card--top .hp-c-big,
.hp-card--top .hp-c-suit { color: #fff !important; }

@keyframes hp-card-in {
  from {
    opacity: 0;
    scale: .84;
    translate: var(--ctx, 0px) calc(var(--cty, 0px) + 55px);
  }
  to {
    opacity: 1;
    scale: 1;
    translate: var(--ctx, 0px) var(--cty, 0px);
  }
}

/* Card internals */
.hp-c-corner {
  position: absolute;
  top: .55rem;
  left: .65rem;
  font-size: .6rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--text);
  text-align: center;
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
}
.hp-c-corner--br {
  top: auto;
  left: auto;
  bottom: .55rem;
  right: .65rem;
  transform: rotate(180deg);
}
.hp-c-big {
  font-size: 3.6rem;
  font-weight: 800;
  font-family: 'Bricolage Grotesque', system-ui, sans-serif;
  color: var(--text);
  line-height: 1;
  letter-spacing: -.04em;
}
.hp-c-big--sm { font-size: 2.6rem; }
.hp-c-suit {
  font-size: 1.35rem;
  line-height: 1;
  color: var(--text);
  margin-top: .05rem;
}
.hp-c-red                  { color: #dc2626 !important; }
:global(.dark) .hp-c-red  { color: #f87171 !important; }

/* Visual caption */
.hp-visual-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: .68rem;
  letter-spacing: .13em;
  text-transform: uppercase;
  color: var(--muted);
}

/* ─── Entrance animation ─── */
.hp-rise {
  animation: hp-rise-in .6s var(--ease-out) both;
  animation-delay: var(--hp-d, 0s);
}
@keyframes hp-rise-in {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0);    }
}
</style>
