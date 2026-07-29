<script setup lang="ts">
import type { OrderDetail } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

const route = useRoute()
const cart = useCartStore()
const { api } = useApi()

const orderNumber = computed(() => (route.query.order_number as string) || '')
const order = ref<OrderDetail | null>(null)
const loading = ref(true)

onMounted(async () => {
  cart.clearCart()

  if (orderNumber.value) {
    try {
      order.value = await api<OrderDetail>(`/shopping/order/${orderNumber.value}`)
    } catch {
    } finally {
      loading.value = false
    }
  } else {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-12">
    <div class="rounded-3xl bg-white p-8 sm:p-12 text-center shadow-xl ring-1 ring-slate-200/80 relative overflow-hidden">
      <div class="absolute top-0 right-0 -mr-16 -mt-16 w-48 h-48 rounded-full bg-teal-50/50 pointer-events-none" />
      <div class="absolute bottom-0 left-0 -ml-16 -mb-16 w-48 h-48 rounded-full bg-emerald-50/50 pointer-events-none" />

      <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 shadow-md">
        <svg class="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <p class="mt-6 text-xs font-black uppercase tracking-widest text-teal-700">Payment Confirmed</p>
      <h1 class="mt-1 text-3xl sm:text-4xl font-black text-slate-900">Thank You for Your Order!</h1>
      <p class="mt-2 text-sm text-slate-500 max-w-md mx-auto">
        Your payment was processed successfully. We've received your order and are getting it ready for shipment.
      </p>

      <div v-if="orderNumber" class="mt-6 inline-flex items-center gap-2 rounded-xl bg-slate-100 px-4 py-2 text-xs font-mono font-bold text-slate-700">
        <span>Order #:</span>
        <span class="text-teal-700 font-extrabold">{{ orderNumber }}</span>
      </div>
      <div v-if="order" class="mt-8 border-t border-slate-100 pt-8 text-left space-y-6">
        <div>
          <h2 class="text-base font-black text-slate-900">Order Items</h2>
          <div class="mt-4 divide-y divide-slate-100 border-t border-b border-slate-100">
            <div
              v-for="item in order.items"
              :key="item.product?.slug || item.unit_price"
              class="py-3 flex items-center justify-between text-sm"
            >
              <div class="flex items-center gap-3">
                <img
                  v-if="item.product?.images?.[0]?.src"
                  :src="item.product.images[0].src"
                  :alt="item.product.name"
                  class="w-12 h-12 rounded-lg object-cover border border-slate-200"
                />
                <div>
                  <p class="font-bold text-slate-900 capitalize">{{ toTitleCase(item.product?.name || 'Product') }}</p>
                  <p class="text-xs text-slate-500">Qty: {{ item.quantity }} &bull; {{ toUSD(item.unit_price) }} each</p>
                </div>
              </div>
              <span class="font-bold text-slate-900">{{ toUSD(Number(item.unit_price) * item.quantity) }}</span>
            </div>
          </div>
        </div>

        <div v-if="order.delivery_address" class="rounded-2xl bg-slate-50/80 p-4 border border-slate-200/80">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Shipping to</p>
          <p class="mt-1 font-bold text-slate-900 text-sm">{{ order.delivery_address.line_1 }}</p>
          <p v-if="order.delivery_address.line_2" class="text-xs text-slate-600">{{ order.delivery_address.line_2 }}</p>
          <p class="text-xs text-slate-500">
            {{ order.delivery_address.city }}, {{ order.delivery_address.state }} &bull; {{ order.delivery_address.zip_code }}
          </p>
        </div>
      </div>

      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <NuxtLink
          to="/products"
          class="rounded-xl bg-teal-700 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 transition"
        >
          Continue Shopping
        </NuxtLink>
        <NuxtLink
          to="/account/orders"
          class="rounded-xl border border-slate-300 px-6 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 transition"
        >
          View My Orders
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
