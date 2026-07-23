import { defineStore } from 'pinia'
import type { CartItem, CartOut } from '~/types/api'

const GUEST_CART_KEY = '16vmart_guest_cart'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartOut[]>([])
  const simpleItems = ref<CartItem[]>([])
  const loading = ref(false)
  const { api } = useApi()
  const auth = useAuthStore()
  const config = useRuntimeConfig()
  const baseURL = config.public.apiUrl as string

  const cartCount = computed(() => simpleItems.value.reduce((sum, item) => sum + item.quantity, 0))
  const cartTotal = computed(() =>
    items.value.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0),
  )

 
  function getGuestCart(): CartItem[] {
    if (import.meta.server) return []
    try {
      const raw = localStorage.getItem(GUEST_CART_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  }

  function saveGuestCart(cartItems: CartItem[]) {
    if (import.meta.server) return
    localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cartItems))
  }

  function clearGuestCart() {
    if (import.meta.server) return
    localStorage.removeItem(GUEST_CART_KEY)
  }


  async function fetchCart() {
    if (!auth.isAuthenticated) {
      simpleItems.value = getGuestCart()
      if (simpleItems.value.length > 0) {
        loading.value = true
        try {
          const fetchedItems: CartOut[] = []
          for (const item of simpleItems.value) {
            try {
              const prod = await $fetch<any>(`${baseURL}/products/${item.product_id}`)
              if (prod) {
                fetchedItems.push({ product: prod, quantity: item.quantity })
              }
            } catch {
            }
          }
          items.value = fetchedItems
        } finally {
          loading.value = false
        }
      } else {
        items.value = []
      }
      return
    }

    loading.value = true
    try {
      const [full, simple] = await Promise.all([
        api<CartOut[]>('/carts'),
        api<CartItem[]>('/carts/simple'),
      ])
      items.value = full
      simpleItems.value = simple
    } catch {
    } finally {
      loading.value = false
    }
  }

  async function addItem(productSlug: string, quantity: number = 1) {
    if (!auth.isAuthenticated) {
      const guest: CartItem[] = getGuestCart() 
      const existing = guest.findIndex(x => x.product_id.toLowerCase() === productSlug.toLowerCase())
      if (existing >= 0 && guest[existing]) {
        guest[existing].quantity  = quantity
      } else {
        guest.push({ product_id: productSlug, quantity })
      }
      saveGuestCart(guest)
      simpleItems.value = guest
      await fetchCart()
      return
    }

    await api('/carts', {
      method: 'POST',
      body: { product_id: productSlug, quantity },
    })
    await fetchCart()
  }

  async function removeItem(productSlug: string) {
    if (!auth.isAuthenticated) {
      const guest = getGuestCart().filter(x => x.product_id.toLowerCase() !== productSlug.toLowerCase())
      saveGuestCart(guest)
      simpleItems.value = guest
      items.value = items.value.filter(x => x.product.slug.toLowerCase() !== productSlug.toLowerCase())
      return
    }

    await api(`/carts/${productSlug}`, { method: 'DELETE' })
    await fetchCart()
  }

  async function updateQuantity(productSlug: string, quantity: number) {
    await addItem(productSlug, quantity)
  }

  /** Push guest cart to server after user authenticates */
  async function syncGuestCartToServer() {
    const guestCart = getGuestCart()
    if (guestCart.length < 1) return

    for (const item of guestCart) {
      try {
        await api('/carts', {
          method: 'POST',
          body: { product_id: item.product_id, quantity: item.quantity },
        })
      } catch {
        // Skip invalid items
      }
    }
    clearGuestCart()
    await fetchCart()
  }

  function clearCart() {
    items.value = []
    simpleItems.value = []
    if (!auth.isAuthenticated) clearGuestCart()
  }

  return {
    items,
    simpleItems,
    loading,
    cartCount,
    cartTotal,
    fetchCart,
    addItem,
    removeItem,
    updateQuantity,
    syncGuestCartToServer,
    clearCart,
  }
})
