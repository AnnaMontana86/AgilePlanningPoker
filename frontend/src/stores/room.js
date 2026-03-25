// Pinia store for live room state.
// Responsible for holding the canonical room snapshot, applying inbound
// SSE events as partial mutations, and managing the EventSource lifecycle
// including exponential-backoff reconnection on network errors.
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useRoomStore = defineStore('room', () => {
  const room = ref(null)
  const eventSource = ref(null)
  const votesResetCount = ref(0)

  const participants = computed(() =>
    room.value ? Object.values(room.value.participants) : []
  )
  const currentRound = computed(() => room.value?.current_round ?? null)
  const isRevealed = computed(() => currentRound.value?.revealed ?? false)
  const cardSet = computed(() => room.value?.card_set ?? null)
  const topics = computed(() => room.value?.topics ?? [])
  const currentTopicIndex = computed(() => room.value?.current_topic_index ?? 0)
  const currentTopic = computed(() => topics.value[currentTopicIndex.value] ?? null)

  function setRoom(data) {
    room.value = data
  }

  function applyEvent(event) {
    if (!room.value) return
    const { type, data } = event

    if (type === 'participant_joined') {
      room.value.participants[data.participant.id] = data.participant
    } else if (type === 'participant_left') {
      delete room.value.participants[data.participant_id]
      if (data.new_owner_id && room.value.participants[data.new_owner_id]) {
        room.value.participants[data.new_owner_id].is_owner = true
      }
    } else if (type === 'vote_cast') {
      // vote_cast sets 'hidden', not the real card — actual values are only
      // known after the 'cards_revealed' event to prevent peeking.
      const p = room.value.participants[data.participant_id]
      if (p) p.vote = 'hidden'
    } else if (type === 'vote_retracted') {
      const p = room.value.participants[data.participant_id]
      if (p) p.vote = null
    } else if (type === 'cards_revealed') {
      room.value.current_round.revealed = true
      for (const [pid, vote] of Object.entries(data.votes)) {
        if (room.value.participants[pid]) {
          room.value.participants[pid].vote = vote
        }
      }
    } else if (type === 'new_round') {
      if (data.estimated_topic) {
        const idx = room.value.topics.findIndex(t => t.id === data.estimated_topic.id)
        if (idx !== -1) room.value.topics[idx] = data.estimated_topic
      }
      room.value.current_round = { revealed: false, number: data.round_number }
      if (data.current_topic_index !== undefined) {
        room.value.current_topic_index = data.current_topic_index
      }
      for (const p of Object.values(room.value.participants)) {
        p.vote = null
      }
    } else if (type === 'music_updated') {
      room.value.music_playing = data.playing
      if (data.volume !== undefined) room.value.music_volume = data.volume
    } else if (type === 'emoji_updated') {
      const p = room.value.participants[data.participant_id]
      if (p) p.emoji = data.emoji
    } else if (type === 'topic_updated') {
      const idx = room.value.topics.findIndex(t => t.id === data.topic.id)
      if (idx !== -1) room.value.topics[idx] = data.topic
    } else if (type === 'topic_added') {
      room.value.topics.push(data.topic)
    } else if (type === 'topics_reordered') {
      room.value.topics = data.topics
    } else if (type === 'topic_removed') {
      room.value.topics = room.value.topics.filter(t => t.id !== data.topic_id)
      room.value.current_topic_index = data.current_topic_index
    } else if (type === 'topic_selected') {
      room.value.current_topic_index = data.current_topic_index
    } else if (type === 'votes_reset') {
      room.value.participants = Object.fromEntries(
        Object.entries(room.value.participants).map(([id, p]) => [id, { ...p, vote: null }])
      )
      // Increment so RoomPage watchers can reset myVote without depending on round number.
      votesResetCount.value++
    } else if (type === 'participant_suspended') {
      const p = room.value.participants[data.participant_id]
      if (p) { p.suspended = true; p.vote = null }
    } else if (type === 'participant_unsuspended') {
      const p = room.value.participants[data.participant_id]
      if (p) p.suspended = false
    } else if (type === 'timer_started') {
      room.value.timer_ends_at = data.ends_at
    } else if (type === 'timer_stopped') {
      room.value.timer_ends_at = null
    } else if (type === 'note_updated') {
      room.value.note = data.note
    }
  }

  let retryDelay = 2000
  let retryTimeout = null

  function connectSSE(roomId) {
    disconnectSSE()

    function connect() {
      const es = new EventSource(`/api/rooms/${roomId}/events`)

      es.onmessage = (e) => {
        try { applyEvent(JSON.parse(e.data)) } catch {}
      }

      es.onopen = () => {
        retryDelay = 2000
      }

      es.onerror = () => {
        es.close()
        retryTimeout = setTimeout(async () => {
          try {
            const res = await fetch(`/api/rooms/${roomId}`)
            if (res.ok) setRoom(await res.json())
          } catch {}
          // Double the delay for the next failure, capped at 30 s.
          retryDelay = Math.min(retryDelay * 2, 30000)
          connect()
        }, retryDelay)
      }

      eventSource.value = es
    }

    connect()
  }

  function disconnectSSE() {
    clearTimeout(retryTimeout)
    retryTimeout = null
    eventSource.value?.close()
    eventSource.value = null
  }

  function clear() {
    disconnectSSE()
    room.value = null
  }

  return {
    room, participants, currentRound, isRevealed, cardSet,
    topics, currentTopicIndex, currentTopic,
    setRoom, applyEvent, connectSSE, disconnectSSE, clear,
    votesResetCount,
  }
})
