import { ref, computed, watch, onBeforeUnmount } from 'vue'

export function useTimer(roomId, roomStore, userStore) {
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

  function startCountdownFrom(endsAt) {
    clearInterval(timerInterval)
    const utcStr = endsAt.endsWith('Z') ? endsAt : endsAt + 'Z'
    const remaining = Math.round((new Date(utcStr) - Date.now()) / 1000)
    if (remaining <= 0) { timerRemaining.value = 0; return }
    timerRemaining.value = remaining
    timerInterval = setInterval(() => {
      timerRemaining.value--
      if (timerRemaining.value <= 0) {
        timerRemaining.value = 0
        clearInterval(timerInterval)
      }
    }, 1000)
  }

  watch(() => roomStore.room?.timer_ends_at, (endsAt) => {
    if (endsAt) {
      startCountdownFrom(endsAt)
    } else {
      clearInterval(timerInterval)
      timerRemaining.value = null
    }
  })

  async function startTimer() {
    if (!timerInput.value || timerInput.value < 1) return
    const seconds = timerUnit.value === 'minutes' ? timerInput.value * 60 : timerInput.value
    timerDialog.value = false
    await fetch(`/api/rooms/${roomId}/timer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: userStore.token, duration_seconds: seconds }),
    })
  }

  async function stopTimer() {
    timerDialog.value = false
    await fetch(`/api/rooms/${roomId}/timer`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: userStore.token }),
    })
  }

  onBeforeUnmount(() => {
    clearInterval(timerInterval)
  })

  return {
    timerDialog, timerInput, timerUnit, timerRemaining,
    formattedTimer, startCountdownFrom, startTimer, stopTimer,
  }
}
