/**
 * Shared helpers for e2e tests.
 * All helpers talk directly to the backend API so tests don't rely
 * on UI flows that are covered by other specs.
 */

const API = 'http://localhost:8000/api'

/**
 * Create a room via the API and return { roomId, token, participantId }.
 */
export async function createRoom(request, {
  ownerNickname = 'Owner',
  roomName = 'Test Room',
  cardSetName = 'Fibonacci',
} = {}) {
  const res = await request.post(`${API}/rooms`, {
    data: { name: roomName, card_set_name: cardSetName, owner_nickname: ownerNickname },
  })
  const body = await res.json()
  return { roomId: body.room_id, token: body.token, participantId: body.participant_id }
}

/**
 * Join an existing room via the API and return { token, participantId }.
 */
export async function joinRoom(request, roomId, nickname) {
  const res = await request.post(`${API}/rooms/${roomId}/join`, {
    data: { nickname },
  })
  const body = await res.json()
  return { token: body.token, participantId: body.participant_id }
}

/**
 * Seed localStorage with a session so the page loads already authenticated.
 */
export async function seedSession(page, { nickname, participantId, token }) {
  await page.addInitScript(({ nickname, participantId, token }) => {
    localStorage.setItem('nickname', nickname)
    localStorage.setItem('participantId', participantId)
    localStorage.setItem('token', token)
  }, { nickname, participantId, token })
}
