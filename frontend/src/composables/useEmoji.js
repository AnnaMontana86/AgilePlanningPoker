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
    document.addEventListener('click', onClickOutsideMood, true)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('click', onClickOutsideMood, true)
  })

  return { EMOJIS, myEmoji, moodOpen, moodAnchor, setEmoji }
}
