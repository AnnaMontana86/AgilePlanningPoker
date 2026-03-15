import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useRoomStore = defineStore('room', () => {
  const room = ref(null)
  const eventSource = ref(null)

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
    } else if (type === 'participant_left' || type === 'participant_kicked') {
      delete room.value.participants[data.participant_id]
      if (data.new_owner_id && room.value.participants[data.new_owner_id]) {
        room.value.participants[data.new_owner_id].is_owner = true
      }
    } else if (type === 'vote_cast') {
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
    }
  }

  function connectSSE(roomId) {
    disconnectSSE()
    const es = new EventSource(`/api/rooms/${roomId}/events`)
    es.onmessage = (e) => {
      try {
        applyEvent(JSON.parse(e.data))
      } catch {
        // malformed event — ignore
      }
    }
    eventSource.value = es
  }

  function disconnectSSE() {
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
  }
})
