import { test, expect } from '@playwright/test'
import { createRoom, joinRoom, seedSession } from './helpers.js'

test.describe('Participant management', () => {
  test('second participant appears in the list via SSE (real-time)', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } = await createRoom(request)

    const ownerCtx = await browser.newContext()
    const ownerPage = await ownerCtx.newPage()
    await ownerPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Owner', participantId: ownerId, token: ownerToken })
    await ownerPage.goto(`/room/${roomId}`)
    await expect(ownerPage.getByText('Round 1')).toBeVisible()

    // Bob joins via API — SSE pushes participant_joined
    await joinRoom(request, roomId, 'Bob')

    await expect(ownerPage.getByText('Bob')).toBeVisible({ timeout: 5000 })

    await ownerCtx.close()
  })

  test('owner can suspend a participant', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } = await createRoom(request)
    await joinRoom(request, roomId, 'Bob')

    const ownerCtx = await browser.newContext()
    const ownerPage = await ownerCtx.newPage()
    await ownerPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Owner', participantId: ownerId, token: ownerToken })
    await ownerPage.goto(`/room/${roomId}`)
    await expect(ownerPage.getByText('Bob')).toBeVisible()

    const bobRow = ownerPage.locator('li', { hasText: 'Bob' })
    await bobRow.hover()
    await bobRow.getByText('Suspend').click()

    // Badge appears and menu item becomes disabled
    await expect(ownerPage.getByText('suspended', { exact: true })).toBeVisible()
    await bobRow.hover()
    await expect(bobRow.getByText('Already suspended')).toBeDisabled()

    await ownerCtx.close()
  })

  test('owner leaving transfers ownership — new owner sees Reveal Cards', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } = await createRoom(request)
    const { token: bobToken, participantId: bobId } = await joinRoom(request, roomId, 'Bob')

    const ownerCtx = await browser.newContext()
    const ownerPage = await ownerCtx.newPage()
    await ownerPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Owner', participantId: ownerId, token: ownerToken })

    const bobCtx = await browser.newContext()
    const bobPage = await bobCtx.newPage()
    await bobPage.addInitScript(({ nickname, participantId, token }) => {
      localStorage.setItem('nickname', nickname)
      localStorage.setItem('participantId', participantId)
      localStorage.setItem('token', token)
    }, { nickname: 'Bob', participantId: bobId, token: bobToken })

    await ownerPage.goto(`/room/${roomId}`)
    await bobPage.goto(`/room/${roomId}`)
    await expect(bobPage.getByText('Round 1')).toBeVisible()

    // Owner leaves
    await ownerPage.getByRole('button', { name: 'Leave' }).click()

    // Bob becomes owner and should now see Reveal Cards
    await expect(bobPage.getByRole('button', { name: 'Reveal Cards' })).toBeVisible({ timeout: 5000 })

    await ownerCtx.close()
    await bobCtx.close()
  })

  test('last participant leaving navigates back to home', async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)

    await page.getByRole('button', { name: 'Leave' }).click()

    await expect(page).toHaveURL('/')
  })
})
