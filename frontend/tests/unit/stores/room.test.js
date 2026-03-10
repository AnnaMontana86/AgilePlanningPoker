import { describe, it, expect } from 'vitest'
import { useRoomStore } from '../../../src/stores/room'

const mockRoom = {
  id: 'room-1',
  name: 'Test Room',
  card_set: { name: 'fibonacci', cards: ['1', '2', '3', '5'] },
  participants: {
    'p1': { id: 'p1', nickname: 'Alice', is_owner: true, vote: null },
    'p2': { id: 'p2', nickname: 'Bob', is_owner: false, vote: null },
  },
  current_round: { number: 1, revealed: false },
}

describe('useRoomStore', () => {
  it('sets room data', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    expect(store.room.id).toBe('room-1')
    expect(store.participants).toHaveLength(2)
  })

  it('participant_joined event adds participant', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({
      type: 'participant_joined',
      data: { participant: { id: 'p3', nickname: 'Carol', is_owner: false, vote: null } },
    })
    expect(store.participants).toHaveLength(3)
  })

  it('participant_kicked event removes participant', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'participant_kicked', data: { participant_id: 'p2' } })
    expect(store.participants).toHaveLength(1)
  })

  it('participant_left event removes participant', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'participant_left', data: { participant_id: 'p2', new_owner_id: null } })
    expect(store.participants).toHaveLength(1)
    expect(store.room.participants['p2']).toBeUndefined()
  })

  it('participant_left with new_owner_id transfers ownership', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'participant_left', data: { participant_id: 'p1', new_owner_id: 'p2' } })
    expect(store.room.participants['p1']).toBeUndefined()
    expect(store.room.participants['p2'].is_owner).toBe(true)
  })

  it('vote_cast marks participant as voted', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'vote_cast', data: { participant_id: 'p2' } })
    expect(store.room.participants['p2'].vote).toBe('hidden')
  })

  it('vote_retracted clears participant vote', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'vote_cast', data: { participant_id: 'p2' } })
    store.applyEvent({ type: 'vote_retracted', data: { participant_id: 'p2' } })
    expect(store.room.participants['p2'].vote).toBeNull()
  })

  it('cards_revealed sets revealed and actual votes', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({
      type: 'cards_revealed',
      data: { votes: { p1: '5', p2: '3' } },
    })
    expect(store.isRevealed).toBe(true)
    expect(store.room.participants['p1'].vote).toBe('5')
    expect(store.room.participants['p2'].vote).toBe('3')
  })

  it('new_round resets votes and increments round number', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.applyEvent({ type: 'cards_revealed', data: { votes: { p1: '5', p2: '3' } } })
    store.applyEvent({ type: 'new_round', data: { round_number: 2 } })
    expect(store.isRevealed).toBe(false)
    expect(store.currentRound.number).toBe(2)
    for (const p of store.participants) {
      expect(p.vote).toBeNull()
    }
  })

  it('new_round updates current_topic_index when provided', () => {
    const store = useRoomStore()
    const roomWithTopics = structuredClone(mockRoom)
    roomWithTopics.topics = [
      { id: 't1', short_name: 'Topic 1', link: '' },
      { id: 't2', short_name: 'Topic 2', link: '' },
    ]
    roomWithTopics.current_topic_index = 0
    store.setRoom(roomWithTopics)
    store.applyEvent({ type: 'new_round', data: { round_number: 2, current_topic_index: 1 } })
    expect(store.currentTopicIndex).toBe(1)
    expect(store.currentTopic.short_name).toBe('Topic 2')
  })

  it('topic_added appends topic', () => {
    const store = useRoomStore()
    const roomWithTopics = structuredClone(mockRoom)
    roomWithTopics.topics = []
    roomWithTopics.current_topic_index = 0
    store.setRoom(roomWithTopics)
    store.applyEvent({ type: 'topic_added', data: { topic: { id: 't1', short_name: 'Sprint 1', link: '' } } })
    expect(store.topics).toHaveLength(1)
    expect(store.topics[0].short_name).toBe('Sprint 1')
  })

  it('topics_reordered replaces topic list', () => {
    const store = useRoomStore()
    const roomWithTopics = structuredClone(mockRoom)
    roomWithTopics.topics = [
      { id: 't1', short_name: 'A', link: '' },
      { id: 't2', short_name: 'B', link: '' },
    ]
    roomWithTopics.current_topic_index = 0
    store.setRoom(roomWithTopics)
    store.applyEvent({ type: 'topics_reordered', data: { topics: [
      { id: 't2', short_name: 'B', link: '' },
      { id: 't1', short_name: 'A', link: '' },
    ]}})
    expect(store.topics[0].short_name).toBe('B')
  })

  it('topic_removed deletes topic and updates index', () => {
    const store = useRoomStore()
    const roomWithTopics = structuredClone(mockRoom)
    roomWithTopics.topics = [
      { id: 't1', short_name: 'A', link: '' },
      { id: 't2', short_name: 'B', link: '' },
    ]
    roomWithTopics.current_topic_index = 1
    store.setRoom(roomWithTopics)
    store.applyEvent({ type: 'topic_removed', data: { topic_id: 't1', current_topic_index: 0 } })
    expect(store.topics).toHaveLength(1)
    expect(store.currentTopicIndex).toBe(0)
  })

  it('clear removes room and disconnects SSE', () => {
    const store = useRoomStore()
    store.setRoom(structuredClone(mockRoom))
    store.clear()
    expect(store.room).toBeNull()
  })
})
