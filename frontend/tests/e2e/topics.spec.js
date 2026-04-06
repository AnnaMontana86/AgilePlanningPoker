import { test, expect } from '@playwright/test'
import { createRoom, seedSession } from './helpers.js'

test.describe('Topic management', () => {
  // TopicsSidebar defaults to open (topicsOpen = ref(true))
  // The add form is shown after clicking the "+" button

  test.beforeEach(async ({ page, request }) => {
    const { roomId, token, participantId } = await createRoom(request)
    await seedSession(page, { nickname: 'Owner', participantId, token })
    await page.goto(`/room/${roomId}`)
    await expect(page.getByText('Round 1')).toBeVisible()
    // Open add-topic form
    await page.getByRole('button', { name: '+' }).click()
  })

  test('owner adds a topic — it appears in the list', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-001')
    await page.getByPlaceholder('Headline').fill('User can log in')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    await expect(page.getByText('US-001').first()).toBeVisible()
    await expect(page.getByText('User can log in', { exact: true })).toBeVisible()
  })

  test('owner adds a topic with a valid link', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-002')
    await page.getByPlaceholder('Headline').fill('Ticket with link')
    await page.getByPlaceholder('Link (optional)').fill('https://jira.example.com/US-002')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    await expect(page.getByText('US-002').first()).toBeVisible()
    // External link rendered as anchor (appears in both sidebar and main area)
    await expect(page.locator('a[href="https://jira.example.com/US-002"]').first()).toBeVisible()
  })

  test('topic with invalid link is rejected', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-003')
    await page.getByPlaceholder('Headline').fill('Bad link topic')
    await page.getByPlaceholder('Link (optional)').fill('not-a-url')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    await expect(page.getByText(/invalid|must start with http/i)).toBeVisible()
    await expect(page.getByText('US-003')).not.toBeVisible()
  })

  test('owner edits a topic headline', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-010')
    await page.getByPlaceholder('Headline').fill('Original headline')
    await page.getByRole('button', { name: 'Add', exact: true }).click()
    await expect(page.getByText('Original headline', { exact: true })).toBeVisible()

    await page.getByTitle('Edit topic').first().click()
    // EditTopicDialog opens
    const headlineInput = page.getByPlaceholder('Headline')
    await headlineInput.clear()
    await headlineInput.fill('Updated headline')
    await page.getByRole('button', { name: 'Save' }).click()

    await expect(page.getByText('Updated headline', { exact: true })).toBeVisible()
    await expect(page.getByText('Original headline', { exact: true })).not.toBeVisible()
  })

  test('owner deletes a topic', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-099')
    await page.getByPlaceholder('Headline').fill('To be deleted')
    await page.getByRole('button', { name: 'Add', exact: true }).click()
    await expect(page.getByText('To be deleted', { exact: true })).toBeVisible()

    await page.getByTitle('Remove topic').first().click()

    await expect(page.getByText('To be deleted', { exact: true })).not.toBeVisible()
  })

  test('switching active topic resets unrevealted votes', async ({ page }) => {
    // Add two topics
    await page.getByPlaceholder('Key').fill('US-A')
    await page.getByPlaceholder('Headline').fill('Topic A')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    await page.getByRole('button', { name: '+' }).click()
    await page.getByPlaceholder('Key').fill('US-B')
    await page.getByPlaceholder('Headline').fill('Topic B')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    // Cast a vote on current topic (Topic A is active)
    await page.getByRole('button', { name: '5', exact: true }).click()
    await expect(page.getByText('✓')).toBeVisible()

    // Switch to Topic B — resets votes
    await page.getByText('Topic B').click()
    await expect(page.getByText('✓')).not.toBeVisible()
  })

  test('CSV download button is visible after topics are added', async ({ page }) => {
    await page.getByPlaceholder('Key').fill('US-CSV')
    await page.getByPlaceholder('Headline').fill('CSV topic')
    await page.getByRole('button', { name: 'Add', exact: true }).click()

    await expect(page.getByTitle('Download CSV')).toBeVisible()
  })
})
