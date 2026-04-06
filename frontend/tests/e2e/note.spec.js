import { test, expect } from '@playwright/test'
import { createRoom, seedSession } from './helpers.js'

test.describe('Shared note', () => {
  // NoteSidebar defaults to open (noteOpen = ref(true))

  test.beforeEach(async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)
    await expect(page.getByText('Round 1')).toBeVisible()
  })

  test('owner writes and saves a markdown note — rendered as HTML', async ({ page }) => {
    await page.getByTitle('Edit note').click()

    await page.getByRole('textbox').fill('## Sprint goal\n\nShip the login feature.')
    await page.getByRole('button', { name: 'Save' }).click()

    // Rendered markdown: heading and paragraph visible
    await expect(page.getByRole('heading', { name: /sprint goal/i })).toBeVisible()
    await expect(page.getByText(/ship the login feature/i)).toBeVisible()
  })

  test('owner can clear the note', async ({ page }) => {
    // Write first
    await page.getByTitle('Edit note').click()
    await page.getByRole('textbox').fill('Temporary note content')
    await page.getByRole('button', { name: 'Save' }).click()
    await expect(page.getByText('Temporary note content')).toBeVisible()

    // Clear it
    await page.getByTitle('Edit note').click()
    await page.getByRole('textbox').clear()
    await page.getByRole('button', { name: 'Save' }).click()

    await expect(page.getByText('Temporary note content')).not.toBeVisible()
  })

  test('cancel editing discards changes', async ({ page }) => {
    await page.getByTitle('Edit note').click()
    await page.getByRole('textbox').fill('I will be discarded')
    await page.getByRole('button', { name: 'Cancel' }).click()

    await expect(page.getByText('I will be discarded')).not.toBeVisible()
  })

  test('note is broadcast to a second participant via SSE', async ({ browser, request }) => {
    const { roomId, token: ownerToken, participantId: ownerId } = await createRoom(request)
    const { token: bobToken, participantId: bobId } = (await import('./helpers.js').then(m =>
      m.joinRoom(request, roomId, 'Bob')
    ))

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

    // Owner saves a note
    await ownerPage.getByTitle('Edit note').click()
    await ownerPage.getByRole('textbox').fill('Shared team note')
    await ownerPage.getByRole('button', { name: 'Save' }).click()

    // Bob sees the note without refresh
    await expect(bobPage.getByText('Shared team note')).toBeVisible({ timeout: 5000 })

    await ownerCtx.close()
    await bobCtx.close()
  })
})
