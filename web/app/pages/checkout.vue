<script setup lang="ts">
import type { Address, AddressIn } from '~/types/api'
import { formatNaira } from '~/lib/money'

definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()
const cart = useCartStore()
const isSubmitting = ref(false)
const useExisting = ref(true)
const selectedAddressId = ref('')
const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Fetch cart and addresses
const addresses = ref<Address[]>([])
const loading = ref(true)

onMounted(async () => {
  await cart.fetchCart()
  try {
    addresses.value = await api<Address[]>('/user/address')
    if (addresses.value.length > 0) {
      selectedAddressId.value = addresses.value[0].address_id
    } else {
      useExisting.value = false
    }
  } catch {
    useExisting.value = false
  }
  loading.value = false
})

// New address form
const { form: newAddress } = useForm<AddressIn>({
  state: '',
  city: '',
  landmark: '',
  line_1: '',
  line_2: '',
  zip_code: 0,
})

async function checkout() {
  clearErrors()
  if (cart.items.length < 1) return

  isSubmitting.value = true
  try {
    const idompotent_key = crypto.randomUUID()
    const items = cart.simpleItems.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
    }))

    const delivery_address = useExisting.value
      ? selectedAddressId.value
      : newAddress.value

    const res = await api<{ success: boolean; url: string }>('/shopping/checkout', {
      method: 'POST',
      body: { idompotent_key, items, delivery_address },
    })

    if (res.url) {
      cart.clearCart()
      window.location.href = res.url
    }
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 py-10">
    <NuxtLink to="/cart" class="text-sm font-semibold text-teal-700">← Back to cart</NuxtLink>
    <h1 class="mt-5 text-4xl font-black">Checkout</h1>

    <div v-if="loading" class="mt-8 space-y-4">
      <div v-for="i in 3" :key="i" class="h-20 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <form v-else class="mt-8 grid gap-8 lg:grid-cols-[1fr_360px]" @submit.prevent="checkout">
      <!-- Left: address -->
      <div class="space-y-6">
        <div
          v-if="errorMessage"
          class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
        >
          {{ errorMessage }}
        </div>

        <section class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 class="text-xl font-black">Delivery address</h2>

          <!-- Toggle -->
          <div v-if="addresses.length" class="mt-4 flex gap-3">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm font-bold"
              :class="useExisting ? 'bg-teal-700 text-white' : 'border border-slate-300'"
              @click="useExisting = true"
            >
              Use saved address
            </button>
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm font-bold"
              :class="!useExisting ? 'bg-teal-700 text-white' : 'border border-slate-300'"
              @click="useExisting = false"
            >
              New address
            </button>
          </div>

          <!-- Existing addresses -->
          <div v-if="useExisting && addresses.length" class="mt-4 space-y-3">
            <label
              v-for="addr in addresses"
              :key="addr.address_id"
              class="flex cursor-pointer items-start gap-3 rounded-xl border p-4"
              :class="selectedAddressId === addr.address_id ? 'border-teal-500 bg-teal-50' : 'border-slate-200'"
            >
              <input
                v-model="selectedAddressId"
                type="radio"
                :value="addr.address_id"
                class="mt-1"
              />
              <div>
                <p class="font-bold">{{ addr.line_1 }}</p>
                <p class="text-sm text-slate-500">
                  {{ addr.city }}, {{ addr.state }} · {{ addr.zip_code }}
                </p>
              </div>
            </label>
          </div>

          <!-- New address form -->
          <div v-if="!useExisting" class="mt-4 space-y-4">
            <div class="grid gap-4 md:grid-cols-2">
              <label class="text-sm font-bold">
                State
                <input v-model="newAddress.state" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
              <label class="text-sm font-bold">
                City
                <input v-model="newAddress.city" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
            </div>
            <label class="block text-sm font-bold">
              Address line 1
              <input v-model="newAddress.line_1" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
            </label>
            <label class="block text-sm font-bold">
              Address line 2 (optional)
              <input v-model="newAddress.line_2" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
            </label>
            <div class="grid gap-4 md:grid-cols-2">
              <label class="text-sm font-bold">
                ZIP code
                <input v-model.number="newAddress.zip_code" type="number" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
              <label class="text-sm font-bold">
                Landmark (optional)
                <input v-model="newAddress.landmark" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
              </label>
            </div>
          </div>
        </section>
      </div>

      <!-- Right: order summary -->
      <div class="h-fit rounded-2xl bg-slate-950 p-6 text-white">
        <h2 class="text-xl font-black">Order summary</h2>
        <div class="mt-4 space-y-3">
          <div
            v-for="item in cart.items"
            :key="item.product.slug"
            class="flex items-center justify-between text-sm"
          >
            <span class="truncate text-slate-300">{{ item.product.name }} × {{ item.quantity }}</span>
            <span class="font-bold">{{ formatNaira(Number(item.product.price) * item.quantity) }}</span>
          </div>
        </div>
        <div class="mt-5 border-t border-slate-700 pt-4">
          <div class="flex items-center justify-between text-lg">
            <span>Total</span>
            <span class="text-2xl font-black">{{ formatNaira(cart.cartTotal) }}</span>
          </div>
        </div>
        <button
          type="submit"
          :disabled="isSubmitting || cart.items.length < 1"
          class="mt-5 w-full rounded-xl bg-teal-500 py-3 font-bold disabled:opacity-60"
        >
          {{ isSubmitting ? 'Processing…' : 'Pay with Stripe' }}
        </button>
        <p class="mt-3 text-center text-xs text-slate-400">
          You'll be redirected to Stripe for secure payment.
        </p>
      </div>
    </form>
  </div>
</template>
