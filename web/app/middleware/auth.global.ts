
export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()
  const accessToken = useCookie('access_token')

  if (accessToken.value && !auth.isAuthenticated) {
    await auth.fetchUser()
  }
})
