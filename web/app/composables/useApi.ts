/**
 * Centralized API composable — wraps $fetch with auth headers,
 * auto-refresh on 401, and consistent error handling.
 */
export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiUrl as string
  const accessToken = useCookie('access_token')

  const headers = computed(() => {
    const h: Record<string, string> = {}
    if (accessToken.value) {
      h['Authorization'] = `Bearer ${accessToken.value}`
    }
    return h
  })

  async function refreshToken(): Promise<boolean> {
    try {
      await $fetch(`${baseURL}/auth/refresh-token`, {
        method: 'POST',
        credentials: 'include',
      })
      return true
    } catch {
      return false
    }
  }

  async function api<T>(
    url: string,
    options: Parameters<typeof $fetch>[1] = {},
  ): Promise<T> {
    const endpoint = url.startsWith('http') ? url : `${baseURL}${url}`

    try {
      return await $fetch<T>(endpoint, {
        ...options,
        headers: {
          ...headers.value,
          ...(options.headers as Record<string, string>),
        },
        credentials: 'include',
      })
    } catch (error: any) {
      const status = error?.response?.status ?? error?.statusCode
      if (status === 401) {
        const refreshed = await refreshToken()
        if (refreshed) {
          return await $fetch<T>(endpoint, {
            ...options,
            headers: {
              ...headers.value,
              ...(options.headers as Record<string, string>),
            },
            credentials: 'include',
          })
        }
        // refresh failed — clear token and redirect to login
        accessToken.value = null
        const currentRoute = useRoute()
        await navigateTo(`/auth/login?redirect=${currentRoute.fullPath}`)
      }
      throw error
    }
  }

  return { api, baseURL, headers, refreshToken }
}
