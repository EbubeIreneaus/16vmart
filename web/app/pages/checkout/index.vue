<script setup lang="ts">
import type { Address, AddressIn } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

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

// Fetch cart and saved addresses
const addresses = ref<Address[]>([])
const loading = ref(true)

onMounted(async () => {
  await cart.fetchCart()
  try {
    addresses.value = await api<Address[]>('/user/address')
    if (addresses.value.length > 0) {
      selectedAddressId.value = addresses.value[0].address_id
      useExisting.value = true
    } else {
      useExisting.value = false
    }
  } catch {
    useExisting.value = false
  } finally {
    loading.value = false
  }
})

// New address form state
const { form: newAddress } = useForm<AddressIn>({
  state: '',
  city: '',
  landmark: '',
  line_1: '',
  line_2: '',
  zip_code: 0,
})

async function handleCheckout() {
  clearErrors()
  if (cart.simpleItems.length < 1 && cart.items.length < 1) {
    setError('Your cart is empty.')
    return
  }

  if (useExisting.value && !selectedAddressId.value) {
    setError('Please select a saved delivery address or enter a new address.')
    return
  }

  isSubmitting.value = true
  try {
    const idompotent_key = crypto.randomUUID()
    const items = cart.simpleItems.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
    }))

    const delivery_address = useExisting.value
      ? selectedAddressId.value
      : {
          state: newAddress.value.state.trim(),
          city: newAddress.value.city.trim(),
          line_1: newAddress.value.line_1.trim(),
          line_2: newAddress.value.line_2?.trim() || null,
          zip_code: Number(newAddress.value.zip_code),
          landmark: newAddress.value.landmark?.trim() || null,
        }

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
    <NuxtLink to="/cart" class="text-sm font-bold text-teal-700 hover:underline">
      &larr; Back to Cart
    </NuxtLink>

    <h1 class="mt-4 text-4xl font-black text-slate-900">Checkout</h1>

    <div v-if="loading" class="mt-8 space-y-4">
      <div v-for="i in 3" :key="i" class="h-20 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <form v-else class="mt-8 grid gap-8 lg:grid-cols-[1fr_360px]" @submit.prevent="handleCheckout">
      <!-- Left Column: Address Selection -->
      <div class="space-y-6">
        <div
          v-if="errorMessage"
          class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-800"
        >
          {{ errorMessage }}
        </div>

        <section class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 class="text-xl font-black text-slate-900">Delivery Address</h2>

          <!-- Address Toggle (Existing vs New) -->
          <div v-if="addresses.length" class="mt-4 flex gap-3">
            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-sm font-bold transition"
              :class="useExisting ? 'bg-teal-700 text-white shadow-xs' : 'border border-slate-300 text-slate-700 hover:bg-slate-50'"
              @click="useExisting = true"
            >
              Saved Address ({{ addresses.length }})
            </button>
            <button
              type="button"
              class="rounded-xl px-4 py-2.5 text-sm font-bold transition"
              :class="!useExisting ? 'bg-teal-700 text-white shadow-xs' : 'border border-slate-300 text-slate-700 hover:bg-slate-50'"
              @click="useExisting = false"
            >
              + New Address
            </button>
          </div>

          <!-- Existing Addresses Radio List -->
          <div v-if="useExisting && addresses.length" class="mt-4 space-y-3">
            <label
              v-for="addr in addresses"
              :key="addr.address_id"
              class="flex cursor-pointer items-start gap-3 rounded-xl border p-4 transition"
              :class="selectedAddressId === addr.address_id ? 'border-teal-600 bg-teal-50/60 ring-1 ring-teal-600/30' : 'border-slate-200 hover:border-slate-300'"
            >
              <input
                v-model="selectedAddressId"
                type="radio"
                name="delivery_address"
                :value="addr.address_id"
                class="mt-1 text-teal-600"
              />
              <div>
                <p class="font-bold text-slate-900 text-sm">{{ addr.line_1 }}</p>
                <p v-if="addr.line_2" class="text-xs text-slate-600">{{ addr.line_2 }}</p>
                <p class="text-xs text-slate-500 mt-1">
                  {{ addr.city }}, {{ addr.state }} &bull; {{ addr.zip_code }}
                </p>
                <p v-if="addr.landmark" class="text-xs text-teal-700 italic mt-0.5">Near: {{ addr.landmark }}</p>
              </div>
            </label>
          </div>

          <!-- New Address Inputs -->
          <div v-if="!useExisting" class="mt-4 space-y-4">
            <div class="grid gap-4 md:grid-cols-2">
              <label class="text-sm font-bold text-slate-800">
                State <span class="text-rose-500">*</span>
                <input v-model="newAddress.state" required class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="e.g. Lagos" />
              </label>
              <label class="text-sm font-bold text-slate-800">
                City <span class="text-rose-500">*</span>
                <input v-model="newAddress.city" required class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="e.g. Ikeja" />
              </label>
            </div>

            <label class="block text-sm font-bold text-slate-800">
              Address Line 1 <span class="text-rose-500">*</span>
              <input v-model="newAddress.line_1" required class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="Street address" />
            </label>

            <label class="block text-sm font-bold text-slate-800">
              Address Line 2 (optional)
              <input v-model="newAddress.line_2" class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="Apartment, suite, unit" />
            </label>

            <div class="grid gap-4 md:grid-cols-2">
              <label class="text-sm font-bold text-slate-800">
                ZIP Code <span class="text-rose-500">*</span>
                <input v-model.number="newAddress.zip_code" type="number" required class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="100001" />
              </label>

              <label class="text-sm font-bold text-slate-800">
                Landmark (optional)
                <input v-model="newAddress.landmark" class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none" placeholder="Nearby landmark" />
              </label>
            </div>
          </div>
        </section>
      </div>

      <!-- Right Column: Order Summary -->
      <div class="h-fit rounded-2xl bg-slate-950 p-6 text-white shadow-xl">
        <h2 class="text-xl font-black border-b border-slate-800 pb-3">Order Summary</h2>
        <div class="mt-4 space-y-3 max-h-64 overflow-y-auto pr-1">
          <div
            v-for="item in cart.items"
            :key="item.product.slug"
            class="flex items-center justify-between text-sm"
          >
            <span class="truncate text-slate-300 font-medium">{{ toTitleCase(item.product.name) }} &times; {{ item.quantity }}</span>
            <span class="font-bold text-white">{{ toUSD(Number(item.product.price) * item.quantity) }}</span>
          </div>
        </div>

        <div class="mt-5 border-t border-slate-800 pt-4">
          <div class="flex items-center justify-between text-base">
            <span class="text-slate-300">Total Due</span>
            <span class="text-2xl font-black text-teal-400">{{ toUSD(cart.cartTotal) }}</span>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isSubmitting || cart.items.length < 1"
          class="mt-6 w-full rounded-xl bg-teal-500 hover:bg-teal-400 py-3.5 font-bold text-slate-950 shadow-md disabled:opacity-60 transition"
        >
          {{ isSubmitting ? 'Redirecting to Stripe...' : 'Pay with Stripe &rarr;' }}
        </button>

        <p class="mt-3 text-center text-xs text-slate-400">
          Secure payment processing handled via Stripe.
        </p>
      </div>
    </form>
  </div>
</template>
