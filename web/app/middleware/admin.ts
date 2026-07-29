/**
 * Admin middleware — checks user is admin or superadmin.
 * Usage: definePageMeta({ middleware: 'admin' })
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

  if (!auth.isAdmin) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Administrator access required.',
    })
  }
})
