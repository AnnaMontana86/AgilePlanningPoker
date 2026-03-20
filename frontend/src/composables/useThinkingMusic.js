import { ref, computed, watch, onBeforeUnmount } from 'vue'

export function useThinkingMusic(roomId, roomStore, userStore, isOwner, allVoted) {
  const thinkingActive = computed(() => roomStore.room?.music_playing ?? false)
  const volumeLevel = ref(0.05)
  const showVolume = ref(false)
  let thinkingAudio = null
  let volumeHideTimer = null
  let volumeDebounceTimer = null

  function onMusicWrapperEnter() {
    clearTimeout(volumeHideTimer)
    showVolume.value = true
  }

  function onMusicWrapperLeave() {
    volumeHideTimer = setTimeout(() => { showVolume.value = false }, 400)
  }

  function startThinkingAudio() {
    if (thinkingAudio) return
    thinkingAudio = new Audio('/sounds/thinking-time.mp3')
    thinkingAudio.loop = true
    thinkingAudio.volume = volumeLevel.value
    thinkingAudio.play()
  }

  function stopThinkingAudio() {
    thinkingAudio?.pause()
    thinkingAudio = null
  }

  async function toggleThinkingMusic() {
    await fetch(`/api/rooms/${roomId}/music`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: userStore.token, playing: !thinkingActive.value, volume: volumeLevel.value }),
    })
  }

  watch(volumeLevel, v => {
    if (thinkingAudio) thinkingAudio.volume = v
    if (isOwner.value && thinkingActive.value) {
      clearTimeout(volumeDebounceTimer)
      volumeDebounceTimer = setTimeout(() => {
        fetch(`/api/rooms/${roomId}/music`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: userStore.token, playing: true, volume: v }),
        }).catch(() => {})
      }, 300)
    }
  })

  watch(() => roomStore.room?.music_volume, (v) => {
    if (v !== undefined && v !== volumeLevel.value) volumeLevel.value = v
  })

  watch(thinkingActive, (playing) => {
    if (playing) startThinkingAudio()
    else stopThinkingAudio()
  })

  watch(allVoted, (voted) => {
    if (voted && thinkingActive.value && isOwner.value) {
      fetch(`/api/rooms/${roomId}/music`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: userStore.token, playing: false }),
      }).catch(() => {})
    }
  })

  onBeforeUnmount(() => {
    clearTimeout(volumeHideTimer)
    clearTimeout(volumeDebounceTimer)
    stopThinkingAudio()
  })

  return {
    thinkingActive, volumeLevel, showVolume,
    onMusicWrapperEnter, onMusicWrapperLeave,
    toggleThinkingMusic, startThinkingAudio, stopThinkingAudio,
  }
}
