import { test, expect } from '@playwright/test'

test.describe('Create room', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('owner lands on RoomPage after creating a room', async ({ page }) => {
    await page.getByPlaceholder('Enter your nickname').fill('Alice')
    await page.getByRole('button', { name: 'Create a room' }).click()

    // Dialog opens — heading "Create a room" appears inside the modal
    await expect(page.getByRole('heading', { name: 'Create a room' })).toBeVisible()

    await page.getByPlaceholder('Room name').fill('Sprint 42')
    await page.locator('select').selectOption('Fibonacci')
    await page.getByRole('button', { name: 'Create Room' }).click()

    await expect(page).toHaveURL(/\/room\//)
    await expect(page.getByText('Round 1')).toBeVisible()
  })

  test('create room with a custom card set', async ({ page }) => {
    await page.getByPlaceholder('Enter your nickname').fill('Alice')
    await page.getByRole('button', { name: 'Create a room' }).click()

    await page.getByPlaceholder('Room name').fill('Custom Cards')
    await page.locator('select').selectOption('__custom__')
    await page.getByPlaceholder('e.g. 1, 2, 3, 5, 8, 13, ?').fill('XS,S,M,L,XL')
    await page.getByRole('button', { name: 'Create Room' }).click()

    await expect(page).toHaveURL(/\/room\//)
    await expect(page.getByRole('button', { name: 'XS' })).toBeVisible()
  })

  test('nickname with semicolon is rejected before dialog opens', async ({ page }) => {
    await page.getByPlaceholder('Enter your nickname').fill('Ali;ce')
    await page.getByRole('button', { name: 'Create a room' }).click()

    // Dialog should NOT open
    await expect(page.getByRole('heading', { name: 'Create a room' })).not.toBeVisible()
  })

  test('room name with semicolon is rejected', async ({ page }) => {
    await page.getByPlaceholder('Enter your nickname').fill('Alice')
    await page.getByRole('button', { name: 'Create a room' }).click()

    await page.getByPlaceholder('Room name').fill('Bad;Name')
    await page.locator('select').selectOption('Fibonacci')
    await page.getByRole('button', { name: 'Create Room' }).click()

    // Error shown, dialog stays open
    await expect(page.getByRole('heading', { name: 'Create a room' })).toBeVisible()
    await expect(page).toHaveURL('/')
  })

  test('custom card set with fewer than 2 cards disables Create Room button', async ({ page }) => {
    await page.getByPlaceholder('Enter your nickname').fill('Alice')
    await page.getByRole('button', { name: 'Create a room' }).click()

    await page.getByPlaceholder('Room name').fill('Test')
    await page.locator('select').selectOption('__custom__')
    await page.getByPlaceholder('e.g. 1, 2, 3, 5, 8, 13, ?').fill('OnlyOne')

    await expect(page.getByRole('button', { name: 'Create Room' })).toBeDisabled()
  })
})
