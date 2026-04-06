import { test, expect } from '@playwright/test'
import { createRoom } from './helpers.js'

test.describe('Join room', () => {
  test('participant joins by room ID and lands on RoomPage', async ({ page, request }) => {
    const { roomId } = await createRoom(request, { ownerNickname: 'Owner' })

    await page.goto('/')
    await page.getByPlaceholder('Enter your nickname').fill('Bob')
    await page.getByRole('button', { name: 'Join a room' }).click()

    await expect(page.getByRole('heading', { name: 'Join a room' })).toBeVisible()
    await page.getByPlaceholder('Room ID or paste invite link').fill(roomId)
    await page.getByRole('button', { name: 'Join Room' }).click()

    await expect(page).toHaveURL(`/room/${roomId}`)
    await expect(page.getByText('Round 1')).toBeVisible()
  })

  test('participant joins via full invite link in join dialog', async ({ page, request }) => {
    const { roomId } = await createRoom(request, { ownerNickname: 'Owner' })
    const inviteLink = `http://localhost:5173/room/${roomId}`

    await page.goto('/')
    await page.getByPlaceholder('Enter your nickname').fill('Carol')
    await page.getByRole('button', { name: 'Join a room' }).click()

    // Paste full invite URL — app extracts the room ID
    await page.getByPlaceholder('Room ID or paste invite link').fill(inviteLink)
    await page.getByRole('button', { name: 'Join Room' }).click()

    await expect(page).toHaveURL(`/room/${roomId}`)
  })

  test('share-link visitor sees join overlay on RoomPage', async ({ page, request }) => {
    const { roomId } = await createRoom(request, { ownerNickname: 'Owner' })

    // Navigate directly without a session — join overlay appears
    await page.goto(`/room/${roomId}`)

    await expect(page.getByPlaceholder('Your nickname')).toBeVisible()
    await page.getByPlaceholder('Your nickname').fill('Dave')
    const joinBtn = page.getByRole('button', { name: 'Join Room' })
    await expect(joinBtn).toBeEnabled()
    await joinBtn.click()

    await expect(page.getByText('Round 1')).toBeVisible()
  })

  test('joining a non-existent room shows an error', async ({ page }) => {
    await page.goto('/')
    await page.getByPlaceholder('Enter your nickname').fill('Bob')
    await page.getByRole('button', { name: 'Join a room' }).click()

    await page.getByPlaceholder('Room ID or paste invite link').fill('does-not-exist')
    await page.getByRole('button', { name: 'Join Room' }).click()

    // Error shown, page stays on homepage
    await expect(page.getByText(/failed to join|not found|error/i)).toBeVisible()
    await expect(page).toHaveURL('/')
  })
})
