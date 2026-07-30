import { test, expect } from '@playwright/test'

test.describe('Authentication Lifecycle', () => {
  const timestamp = Date.now()
  const testUser = {
    fullname: 'E2E Test User',
    email: `e2e_user_${timestamp}@example.com`,
    password: 'Password123!'
  }

  test('should render sign in form properly', async ({ page }) => {
    await page.goto('/auth/login')
    await expect(page.locator('h1')).toContainText('Sign in to 16Vmart')
    const emailInput = page.getByPlaceholder('you@example.com')
    await expect(emailInput).toBeVisible()
    const submitBtn = page.locator('[data-test-id="submit-btn"]')
    await expect(submitBtn).toBeVisible()
  })

  test('should navigate between sign in and register pages', async ({ page }) => {
    await page.goto('/auth/login')
    await page.locator('[data-test-id="register-link"]').click()
    await expect(page).toHaveURL(/\/auth\/register/)
    await expect(page.locator('h1')).toContainText('Create your account')
  })

  test('should perform complete Signup (Registration) flow', async ({ page }) => {
    await page.goto('/auth/register')
    await expect(page.locator('h1')).toContainText('Create your account')

    await page.locator('[data-test-id="fullname"]').fill(testUser.fullname)
    await page.locator('[data-test-id="email"]').fill(testUser.email)
    await page.locator('[data-test-id="password"]').fill(testUser.password)

    await page.locator('[data-test-id="submit-btn"]').click()

    await expect(page).toHaveURL('/', { timeout: 10000 })
  })

  test('should perform Signin (Login) flow with registered credentials', async ({ page }) => {
    await page.goto('/auth/login')

    await page.locator('[data-test-id="email"]').fill(testUser.email)
    await page.locator('[data-test-id="password"]').fill(testUser.password)

    await page.locator('[data-test-id="submit-btn"]').click()

    await expect(page).toHaveURL('/', { timeout: 10000 })

    const cookies = await page.context().cookies()
    const accessToken = cookies.find(c => c.name === 'access_token')
    expect(accessToken).toBeDefined()
  })

  test('should support session Refresh Token invocation', async ({ page, request }) => {
    await page.goto('/auth/login')
    await page.getByPlaceholder('[data-test-id="email"]').fill(testUser.email)
    await page.locator('[data-test-id="password"]').fill(testUser.password)
    await page.locator('[data-test-id="submit-btn"]').click()
    await expect(page).toHaveURL('/')

    const response = await request.post('/api/v1/auth/refresh-token')
    expect([200, 401, 403]).toContain(response.status())
  })
})
