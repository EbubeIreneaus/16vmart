/**
 * Seller middleware — checks user is a seller, admin, or superadmin.
 * Usage: definePageMeta({ middleware: 'seller' })
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

  if (!auth.isSeller) {
    throw createError({
      statusCode: 403,
      statusMessage: 'You need a seller account to access this page.',
    })
  }
})
