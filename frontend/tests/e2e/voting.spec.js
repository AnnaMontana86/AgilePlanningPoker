import { test, expect } from '@playwright/test'
import { createRoom, joinRoom, seedSession } from './helpers.js'

test.describe('Voting round', () => {
  test('owner casts a vote — checkmark appears in participant list', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })

    await page.goto(`/room/${roomId}`)
    await expect(page.getByText('Round 1')).toBeVisible()

    await page.getByRole('button', { name: '5', exact: true }).click()

    // Vote registered — owner row shows ✓
    await expect(page.getByText('✓')).toBeVisible()
  })

  test('owner retracts a vote by clicking the selected card again', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })

    await page.goto(`/room/${roomId}`)
    await page.getByRole('button', { name: '5', exact: true }).click()
    await expect(page.getByText('✓')).toBeVisible()

    await page.getByRole('button', { name: '5', exact: true }).click()
    await expect(page.getByText('✓')).not.toBeVisible()
  })

  test('"Reveal Cards" is disabled until all active participants have voted', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await joinRoom(request, roomId, 'Bob')

    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)

    const revealBtn = page.getByRole('button', { name: 'Reveal Cards' })
    await expect(revealBtn).toBeDisabled()

    // Owner votes — still disabled because Bob hasn't voted
    await page.getByRole('button', { name: '8', exact: true }).click()
    await expect(revealBtn).toBeDisabled()
  })

  test('two participants vote and owner reveals — votes and results shown', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } = await createRoom(request)
    const { token: bobToken, participantId: bobId } = await joinRoom(request, roomId, 'Bob')

    const ownerCtx = await browser.newContext()
    const ownerPage = await ownerCtx.newPage()
    await ownerPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Owner', participantId: ownerId, token: ownerToken })
    await ownerPage.goto(`/room/${roomId}`)

    const bobCtx = await browser.newContext()
    const bobPage = await bobCtx.newPage()
    await bobPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Bob', participantId: bobId, token: bobToken })
    await bobPage.goto(`/room/${roomId}`)

    // Both vote
    await ownerPage.getByRole('button', { name: '8', exact: true }).click()
    await bobPage.getByRole('button', { name: '5', exact: true }).click()

    // Owner reveals
    const revealBtn = ownerPage.getByRole('button', { name: 'Reveal Cards' })
    await expect(revealBtn).toBeEnabled({ timeout: 5000 })
    await revealBtn.click()

    // Wait for cards to be hidden (confirms isRevealed=true), then check vote values
    await expect(ownerPage.getByText('Your vote')).not.toBeVisible({ timeout: 5000 })
    await expect(ownerPage.getByText('8', { exact: true })).toBeVisible()
    await expect(ownerPage.getByText('5', { exact: true })).toBeVisible()
    await expect(bobPage.getByText('8', { exact: true })).toBeVisible()

    // Summary stats appear
    await expect(ownerPage.getByText(/average|most popular/i)).toBeVisible()

    await ownerCtx.close()
    await bobCtx.close()
  })

  test('owner advances to next round — round counter increments and vote clears', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)

    await page.getByRole('button', { name: '3', exact: true }).click()
    await page.getByRole('button', { name: 'Reveal Cards' }).click()
    await page.getByRole('button', { name: 'Next Topic' }).click()

    await expect(page.getByText('Round 2')).toBeVisible()
    // ✓ is gone — vote was cleared
    await expect(page.getByText('✓')).not.toBeVisible()
  })

  test('owner can revote — round stays the same, vote clears', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)

    await page.getByRole('button', { name: '13', exact: true }).click()
    await page.getByRole('button', { name: 'Reveal Cards' }).click()
    const revoteBtn = page.getByRole('button', { name: 'Revote' })
    await expect(revoteBtn).toBeVisible()
    await revoteBtn.click()

    // After retry, Revote button disappears (isRevealed → false) and no vote checkmark
    await expect(revoteBtn).not.toBeVisible()
    await expect(page.getByText('✓')).not.toBeVisible()
  })
})
