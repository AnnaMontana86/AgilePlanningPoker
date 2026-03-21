// Composable for the participant mood / emoji reaction feature.
// Responsible for managing the emoji picker state, toggling the selected
// emoji (clicking the active emoji again clears it), and closing the
// picker on outside clicks.
import { ref, onMounted, onBeforeUnmount } from 'vue'

export function useEmoji(roomId, userStore, apiFetch, error) {
  const EMOJIS = ['🤔', '😄', '😢', '❤️', '☕', '🍺']
  const myEmoji = ref(null)
  const moodOpen = ref(false)
  const moodAnchor = ref(null)

  function onClickOutsideMood(e) {
    if (moodAnchor.value && !moodAnchor.value.contains(e.target)) {
      moodOpen.value = false
    }
  }

  async function setEmoji(emoji) {
    // Tapping the already-active emoji sends null — works as a toggle to clear it.
    const next = myEmoji.value === emoji ? null : emoji
    myEmoji.value = next
    try {
      await apiFetch(`/api/rooms/${roomId}/emoji`, 'POST', {
        participant_id: userStore.participantId,
        emoji: next,
      })
    } catch (e) {
      myEmoji.value = myEmoji.value === null ? emoji : null
      error.value = e.message
    }
  }

  onMounted(() => {
    // Capture phase (true) intercepts the click before child elements consume it.
    document.addEventListener('click', onClickOutsideMood, true)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('click', onClickOutsideMood, true)
  })

  return { EMOJIS, myEmoji, moodOpen, moodAnchor, setEmoji }
}
