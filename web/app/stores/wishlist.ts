import { defineStore } from 'pinia'

export const useWishlistStore = defineStore('wishlist', () => {
  const ids = ref<string[]>([])
  const loading = ref(false)
  const { api } = useApi()
  const auth = useAuthStore()

  function isWishlisted(slug: string): boolean {
    return ids.value.includes(slug.toLowerCase())
  }

  async function fetchIds() {
    if (!auth.isAuthenticated) {
      ids.value = []
      return
    }
    try {
      ids.value = await api<string[]>('/wishlists/ids')
    } catch {
      ids.value = []
    }
  }

  async function add(slug: string) {
    if (!auth.isAuthenticated) {
      await navigateTo(`/auth/login?redirect=${useRoute().fullPath}`)
      return
    }
    await api('/wishlists', {
      method: 'POST',
      body: { product_id: slug },
    })
    if (!ids.value.includes(slug.toLowerCase())) {
      ids.value.push(slug.toLowerCase())
    }
  }

  async function remove(slug: string) {
    await api(`/wishlists/${slug}`, { method: 'DELETE' })
    ids.value = ids.value.filter(id => id !== slug.toLowerCase())
  }

  async function toggle(slug: string) {
    if (isWishlisted(slug)) {
      await remove(slug)
    } else {
      await add(slug)
    }
  }

  return {
    ids,
    loading,
    isWishlisted,
    fetchIds,
    add,
    remove,
    toggle,
  }
})
