import { ref } from 'vue'

export function useJoinFlow(roomId, roomStore, userStore, router) {
  const joining = ref(false)
  const joinNickname = ref(userStore.nickname ?? '')
  const joinError = ref('')

  async function joinRoom() {
    if (!joinNickname.value.trim()) return
    if (joinNickname.value.includes(';')) {
      joinError.value = 'Nickname must not contain ";".'
      return
    }
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

  return { joining, joinNickname, joinError, joinRoom }
}
