import { test, expect } from '@playwright/test'
import { createRoom, seedSession } from './helpers.js'

test.describe('Timer', () => {
  test.beforeEach(async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)
    await expect(page.getByText('Round 1')).toBeVisible()
  })

  test('owner starts a 30-second timer — countdown appears in toolbar', async ({ page }) => {
    await page.getByRole('button', { name: 'Timer' }).click()
    await expect(page.getByText('Set Timer')).toBeVisible()

    await page.getByPlaceholder('Duration').fill('30')
    await page.locator('select').selectOption('seconds')
    await page.getByRole('button', { name: 'Start' }).click()

    // Countdown in MM:SS format appears in toolbar
    await expect(page.getByText(/\d{2}:\d{2}/)).toBeVisible({ timeout: 3000 })
  })

  test('owner stops an active timer — countdown disappears', async ({ page }) => {
    await page.getByRole('button', { name: 'Timer' }).click()
    await page.getByPlaceholder('Duration').fill('5')
    await page.locator('select').selectOption('minutes')
    await page.getByRole('button', { name: 'Start' }).click()
    await expect(page.getByText(/\d{2}:\d{2}/)).toBeVisible({ timeout: 3000 })

    // Reopen and delete
    await page.getByRole('button', { name: 'Timer' }).click()
    await page.getByRole('button', { name: 'Delete Timer' }).click()

    await expect(page.getByText(/\d{2}:\d{2}/)).not.toBeVisible()
  })

  test('Start button is disabled when duration is 0', async ({ page }) => {
    await page.getByRole('button', { name: 'Timer' }).click()
    await page.getByPlaceholder('Duration').fill('0')

    await expect(page.getByRole('button', { name: 'Start' })).toBeDisabled()
  })
})
