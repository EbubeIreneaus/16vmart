import { defineStore } from 'pinia'
import type { User } from '~/types/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const config = useRuntimeConfig()
  const baseURL = config.public.apiUrl as string
  const accessToken = useCookie('access_token')

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'superadmin')
  const isSuperAdmin = computed(() => user.value?.role === 'superadmin')
  const isSeller = computed(() =>
    user.value?.role === 'seller' || user.value?.role === 'admin' || user.value?.role === 'superadmin',
  )

  function parseJwtUser(token?: string | null): User | null {
    if (!token) return null
    try {
      const parts = token.split('.')
      if (parts.length < 2) return null
      const payload = JSON.parse(atob(parts[1] as string))
      return {
        id: Number(payload.sub),
        fullname: payload.fullname || '',
        email: payload.email || '',
        email_verified: true,
        role: payload.role || 'user',
        status: 'active',
      }
    } catch {
      return null
    }
  }

  async function fetchUser() {
    if (accessToken.value) {
      const parsed = parseJwtUser(accessToken.value)
      if (parsed) {
        user.value = parsed
      }
    }

    if (!accessToken.value && !useCookie('refresh_token').value) {
      user.value = null
      return
    }

    try {
      await $fetch(`${baseURL}/auth/refresh-token`, {
        method: 'POST',
        credentials: 'include',
      })
      const newToken = useCookie('access_token').value || accessToken.value
      if (newToken) {
        const parsed = parseJwtUser(newToken)
        if (parsed) {
          user.value = parsed
        }
      }
    } catch {
      if (!user.value) {
        accessToken.value = null
      }
    }
  }

  function setUser(u: User) {
    user.value = u
  }

  async function login(email: string, password: string) {
    await $fetch(`${baseURL}/auth/signin`, {
      method: 'POST',
      body: { email, password },
      credentials: 'include',
    })
    const token = useCookie('access_token').value
    if (token) {
      const parsed = parseJwtUser(token)
      if (parsed) {
        user.value = parsed
      }
    }
  }

  async function register(fullname: string, email: string, password: string) {
    await $fetch(`${baseURL}/auth/signup`, {
      method: 'POST',
      body: { fullname, email, password },
      credentials: 'include',
    })
    const token = useCookie('access_token').value
    if (token) {
      const parsed = parseJwtUser(token)
      if (parsed) {
        user.value = parsed
      }
    }
  }

  async function logout() {
    try {
      await $fetch(`${baseURL}/auth/signout`, {
        method: 'POST',
        credentials: 'include',
      })
    } catch {
      // ignore network errors during signout
    } finally {
      user.value = null
      accessToken.value = null
      const refreshToken = useCookie('refresh_token')
      refreshToken.value = null
      await navigateTo('/')
    }
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    isSuperAdmin,
    isSeller,
    fetchUser,
    setUser,
    login,
    register,
    logout,
  }
})
