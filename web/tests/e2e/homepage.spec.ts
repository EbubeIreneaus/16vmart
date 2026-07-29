import { test, expect } from '@playwright/test'

test.describe('Homepage', () => {
  test('should render hero section and main heading', async ({ page }) => {
    await page.goto('/')

    await expect(page.locator('h1')).toContainText('Find what moves your world.')

    const exploreLink = page.getByRole('link', { name: 'Explore the marketplace' })
    await expect(exploreLink).toBeVisible()
    await expect(exploreLink).toHaveAttribute('href', '/products')
  })

  test('should display department section and seller banner', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByText('SHOP BY DEPARTMENT')).toBeVisible()

    await expect(page.getByText('Turn your inventory into a storefront.')).toBeVisible()
    const startSellingBtn = page.getByRole('link', { name: 'Start selling' })
    await expect(startSellingBtn).toBeVisible()
    await expect(startSellingBtn).toHaveAttribute('href', '/seller')
  })
})
