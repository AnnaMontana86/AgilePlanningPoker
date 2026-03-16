import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import RoomPage from '../../../src/pages/RoomPage.vue'
import { useRoomStore } from '../../../src/stores/room'
import { useUserStore } from '../../../src/stores/user'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { roomId: 'room-1' } }),
  useRouter: () => ({ push: vi.fn() }),
}))

const mockRoom = (overrides = {}) => ({
  id: 'room-1',
  name: 'Test Room',
  card_set: { name: 'fibonacci', cards: ['1', '2', '3', '5'] },
  participants: {
    p1: { id: 'p1', nickname: 'Alice', is_owner: true, vote: null },
    p2: { id: 'p2', nickname: 'Bob', is_owner: false, vote: null },
  },
  current_round: { number: 1, revealed: false },
  music_playing: false,
  topics: [],
  current_topic_index: 0,
  ...overrides,
})

function stubGlobals() {
  vi.stubGlobal('EventSource', class {
    constructor() { this.close = vi.fn() }
  })
  vi.stubGlobal('Audio', class {
    constructor() { this.loop = false; this.volume = 1; this.play = vi.fn(); this.pause = vi.fn() }
  })
  vi.stubGlobal('fetch', vi.fn())
}

async function mountWithRoom(room) {
  global.fetch.mockResolvedValue({
    ok: true,
    json: async () => room,
  })

  const pinia = createPinia()
  setActivePinia(pinia)

  const userStore = useUserStore()
  userStore.setSession('p1', 'tok-1')

  const roomStore = useRoomStore()
  roomStore.setRoom(room)

  const wrapper = mount(RoomPage, {
    global: { plugins: [pinia] },
  })

  await flushPromises()
  await nextTick()

  return { wrapper, roomStore }
}

describe('Thinking time button', () => {
  beforeEach(() => {
    stubGlobals()
  })

  it('is enabled when not all participants have voted', async () => {
    const room = mockRoom()  // both votes null
    const { wrapper } = await mountWithRoom(room)

    const btn = wrapper.findAll('button').find(b => b.text().includes('Thinking time'))
    expect(btn).toBeDefined()
    expect(btn.attributes('disabled')).toBeUndefined()
  })

  it('is disabled when all participants have voted and music is off', async () => {
    const room = mockRoom({
      participants: {
        p1: { id: 'p1', nickname: 'Alice', is_owner: true, vote: 'hidden' },
        p2: { id: 'p2', nickname: 'Bob', is_owner: false, vote: 'hidden' },
      },
    })
    const { wrapper } = await mountWithRoom(room)

    const btn = wrapper.findAll('button').find(b => b.text().includes('Thinking time'))
    expect(btn).toBeDefined()
    expect(btn.attributes('disabled')).toBeDefined()
  })

  it('remains enabled (stop) when all voted but music is already playing', async () => {
    const room = mockRoom({
      participants: {
        p1: { id: 'p1', nickname: 'Alice', is_owner: true, vote: 'hidden' },
        p2: { id: 'p2', nickname: 'Bob', is_owner: false, vote: 'hidden' },
      },
      music_playing: true,
    })
    const { wrapper } = await mountWithRoom(room)

    const btn = wrapper.findAll('button').find(b => b.text().includes('Stop Music'))
    expect(btn).toBeDefined()
    expect(btn.attributes('disabled')).toBeUndefined()
  })

  it('sets audio volume to 0.05 when music starts', async () => {
    let audioInstance = null
    vi.stubGlobal('Audio', class {
      constructor() {
        this.loop = false
        this.volume = 1
        this.play = vi.fn()
        this.pause = vi.fn()
        audioInstance = this
      }
    })

    const room = mockRoom({ music_playing: true })
    await mountWithRoom(room)

    expect(audioInstance).not.toBeNull()
    expect(audioInstance.volume).toBe(0.05)
  })

  it('shows volume slider on mouseenter when music is playing', async () => {
    const room = mockRoom({ music_playing: true })
    const { wrapper } = await mountWithRoom(room)

    const hoverDiv = wrapper.find('[data-testid="thinking-music-wrapper"]')
    await hoverDiv.trigger('mouseenter')
    await nextTick()

    expect(wrapper.find('input[type="range"]').exists()).toBe(true)
  })

  it('does not show volume slider on mouseenter when music is off', async () => {
    const room = mockRoom({ music_playing: false })
    const { wrapper } = await mountWithRoom(room)

    const hoverDiv = wrapper.find('[data-testid="thinking-music-wrapper"]')
    await hoverDiv.trigger('mouseenter')
    await nextTick()

    expect(wrapper.find('input[type="range"]').exists()).toBe(false)
  })
})
