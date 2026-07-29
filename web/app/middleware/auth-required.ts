/**
 * Named auth guard — redirects unauthenticated users to login.
 * Usage: definePageMeta({ middleware: 'auth-required' })
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  const accessToken = useCookie('access_token')

  if (!accessToken.value) {
    return navigateTo(`/auth/login?redirect=${to.fullPath}`)
  }

  if (!auth.isAuthenticated) {
    await auth.fetchUser()
  }

  if (!auth.isAuthenticated) {
    return navigateTo(`/auth/login?redirect=${to.fullPath}`)
  }
})
