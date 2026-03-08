import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const nickname = ref(localStorage.getItem('nickname') ?? '')
  const participantId = ref(localStorage.getItem('participantId') ?? '')
  const token = ref(localStorage.getItem('token') ?? '')

  function setNickname(value) {
    nickname.value = value
    localStorage.setItem('nickname', value)
  }

  function setSession(id, tok) {
    participantId.value = id
    token.value = tok
    localStorage.setItem('participantId', id)
    localStorage.setItem('token', tok)
  }

  function clearSession() {
    participantId.value = ''
    token.value = ''
    localStorage.removeItem('participantId')
    localStorage.removeItem('token')
  }

  // Future: Keycloak integration will replace nickname/token with JWT claims
  // const authUser = ref(null)

  return { nickname, participantId, token, setNickname, setSession, clearSession }
})
