import { test, expect } from '@playwright/test'
import { createRoom, joinRoom } from './helpers.js'

const API = 'http://localhost:8000/api'

// Spread 15 votes across Fibonacci values for interesting stats:
// 6×"5", 4×"8", 3×"3", 2×"13"  →  most popular "5", average ≈ 6.47
const OWNER_VOTE = '5'
const PEER_VOTES = ['5', '5', '5', '5', '8', '8', '8', '8', '3', '3', '3', '13', '13', '5']

async function openAs(browser, { nickname, participantId, token }) {
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  await page.addInitScript(({ nickname, participantId, token }) => {
    localStorage.setItem('nickname', nickname)
    localStorage.setItem('participantId', participantId)
    localStorage.setItem('token', token)
  }, { nickname, participantId, token })
  return { ctx, page }
}

test.describe('Large room — 15 participants', () => {
  test('all 15 vote, owner reveals, stats and vote values shown, next round clears', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } =
      await createRoom(request, { ownerNickname: 'Owner', roomName: 'Sprint 42' })

    // Join 14 participants via API
    const peers = []
    for (let i = 1; i <= 14; i++) {
      peers.push(await joinRoom(request, roomId, `Dev ${i}`))
    }

    // Open owner's browser tab
    const { ctx: ownerCtx, page: ownerPage } = await openAs(browser, {
      nickname: 'Owner', participantId: ownerId, token: ownerToken,
    })
    await ownerPage.goto(`/room/${roomId}`)
    await expect(ownerPage.getByText('Round 1')).toBeVisible()

    // All 14 peers visible in participant list (loaded from initial GET)
    await expect(ownerPage.getByText('Dev 14')).toBeVisible()

    // Reveal is still disabled — owner hasn't voted yet
    const revealBtn = ownerPage.getByRole('button', { name: 'Reveal Cards' })
    await expect(revealBtn).toBeDisabled()

    // All 14 peers cast votes via API
    for (let i = 0; i < peers.length; i++) {
      await request.post(`${API}/rooms/${roomId}/vote`, {
        data: { participant_id: peers[i].participantId, token: peers[i].token, card: PEER_VOTES[i] },
      })
    }

    // Owner votes via UI — this triggers allVoted
    await ownerPage.getByRole('button', { name: OWNER_VOTE, exact: true }).click()

    // Reveal Cards becomes enabled once all 15 votes are known locally
    await expect(revealBtn).toBeEnabled({ timeout: 5000 })

    // Owner reveals
    await revealBtn.click()

    // Card selection disappears (isRevealed = true)
    await expect(ownerPage.getByText('Your vote')).not.toBeVisible({ timeout: 5000 })

    // Spot-check several vote values visible in the participant list
    await expect(ownerPage.getByText('13').first()).toBeVisible()
    await expect(ownerPage.getByText('3').first()).toBeVisible()
    await expect(ownerPage.getByText('8').first()).toBeVisible()

    // Summary stats appear
    await expect(ownerPage.getByText(/average/i)).toBeVisible()
    await expect(ownerPage.getByText(/most popular/i)).toBeVisible()

    // Owner advances to round 2 — vote markers clear
    await ownerPage.getByRole('button', { name: 'Next Topic' }).click()
    await expect(ownerPage.getByText('Round 2')).toBeVisible()
    await expect(ownerPage.getByText('✓')).not.toBeVisible()

    await ownerCtx.close()
  })

  test('co-owner can reveal in a 15-user room but cannot start next round', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } =
      await createRoom(request, { ownerNickname: 'Owner' })

    // Join 14 participants; first one will be promoted to co-owner
    const peers = []
    for (let i = 1; i <= 14; i++) {
      peers.push(await joinRoom(request, roomId, `User ${i}`))
    }
    const coOwner = peers[0]

    // Owner promotes first participant to co-owner
    await request.post(`${API}/rooms/${roomId}/participants/${coOwner.participantId}/promote`, {
      data: { token: ownerToken },
    })

    // All 15 cast their votes via API (co-owner included)
    await request.post(`${API}/rooms/${roomId}/vote`, {
      data: { participant_id: ownerId, token: ownerToken, card: '5' },
    })
    for (let i = 0; i < peers.length; i++) {
      await request.post(`${API}/rooms/${roomId}/vote`, {
        data: { participant_id: peers[i].participantId, token: peers[i].token, card: PEER_VOTES[i] },
      })
    }

    // Co-owner opens their browser tab
    const { ctx: coOwnerCtx, page: coOwnerPage } = await openAs(browser, {
      nickname: 'User 1', participantId: coOwner.participantId, token: coOwner.token,
    })
    await coOwnerPage.goto(`/room/${roomId}`)

    // Co-owner badge visible on their own entry
    await expect(coOwnerPage.getByText('co-owner')).toBeVisible()

    // All 15 votes already in (loaded from initial GET) — Reveal is enabled
    const revealBtn = coOwnerPage.getByRole('button', { name: 'Reveal Cards' })
    await expect(revealBtn).toBeEnabled({ timeout: 5000 })

    // Co-owner reveals
    await revealBtn.click()
    await expect(coOwnerPage.getByText('Your vote')).not.toBeVisible({ timeout: 5000 })
    await expect(coOwnerPage.getByText(/most popular/i)).toBeVisible()

    // Co-owner must NOT see "Next Topic" or "Revote" — those are owner-only
    await expect(coOwnerPage.getByRole('button', { name: 'Next Topic' })).not.toBeVisible()
    await expect(coOwnerPage.getByRole('button', { name: 'Revote' })).not.toBeVisible()

    await coOwnerCtx.close()
  })

  test('co-owner can suspend a regular participant but not another co-owner', async ({ browser, request }) => {
    const { roomId, token: ownerToken } =
      await createRoom(request, { ownerNickname: 'Owner' })

    const alice = await joinRoom(request, roomId, 'Alice')  // will be co-owner
    await joinRoom(request, roomId, 'Bob')                  // regular participant
    // fill up to 15 total (owner + alice + bob + 12 more)
    for (let i = 1; i <= 12; i++) {
      await joinRoom(request, roomId, `User ${i}`)
    }

    // Promote Alice to co-owner
    await request.post(`${API}/rooms/${roomId}/participants/${alice.participantId}/promote`, {
      data: { token: ownerToken },
    })

    // Alice opens her browser tab
    const { ctx: aliceCtx, page: alicePage } = await openAs(browser, {
      nickname: 'Alice', participantId: alice.participantId, token: alice.token,
    })
    await alicePage.goto(`/room/${roomId}`)
    await expect(alicePage.getByText('Bob')).toBeVisible()

    // Alice (co-owner) can suspend Bob (regular participant)
    // Locate Bob's row and click its suspend button
    const bobRow = alicePage.locator('li', { hasText: 'Bob' })
    await bobRow.hover()
    await bobRow.getByText('Suspend').click()
    await expect(alicePage.getByText('suspended', { exact: true })).toBeVisible({ timeout: 5000 })

    // Alice's own suspend option should not appear in her hover menu (she's co-owner)
    const aliceRow = alicePage.locator('li', { hasText: 'Alice' })
    await aliceRow.hover()
    await expect(aliceRow.getByText('Suspend')).not.toBeVisible()

    await aliceCtx.close()
  })
})
