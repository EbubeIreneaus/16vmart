import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('should navigate from home to products page', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Explore the marketplace')
    await expect(page).toHaveURL(/\/products/)
  })

  test('should navigate from home to categories page', async ({ page }) => {
    await page.goto('/')
    await page.click('text=All categories →')
    await expect(page).toHaveURL(/\/categories/)
  })

  test('should navigate from home to seller page', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Start selling')
    await expect(page).toHaveURL(/\/seller/)
  })
})
