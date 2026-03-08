import { describe, it, expect, beforeEach } from 'vitest'
import { useUserStore } from '../../../src/stores/user'

describe('useUserStore', () => {
  it('sets and persists nickname', () => {
    const store = useUserStore()
    store.setNickname('Alice')
    expect(store.nickname).toBe('Alice')
    expect(localStorage.getItem('nickname')).toBe('Alice')
  })

  it('sets and persists session', () => {
    const store = useUserStore()
    store.setSession('pid-123', 'tok-abc')
    expect(store.participantId).toBe('pid-123')
    expect(store.token).toBe('tok-abc')
  })

  it('clears session', () => {
    const store = useUserStore()
    store.setSession('pid-123', 'tok-abc')
    store.clearSession()
    expect(store.participantId).toBe('')
    expect(store.token).toBe('')
  })
})
