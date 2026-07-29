<script setup lang="ts">
import type { AdminOrderDetail } from '~/types/api'
import { toUSD } from '~/lib/money'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const router = useRouter()
const { api } = useApi()

const orderNumber = computed(() => String(route.params.order_number))

const { data: order, pending, error, refresh } = await useAsyncData(
  `admin-order-${orderNumber.value}`,
  () => api<AdminOrderDetail>(`/admin/orders/${orderNumber.value}`)
)

const orderStatusOptions = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', 'failed']
const vendorStatusOptions = ['unpaid', 'paid']

async function updateOrderStatus(newStatus: string) {
  if (!order.value) return
  await api(`/admin/orders/status/${orderNumber.value}`, {
    method: 'PATCH',
    body: { status: newStatus },
  })
  order.value.status = newStatus as any
  await refresh()
}

async function updateVendorStatus(vid: string, newStatus: string) {
  if (!order.value) return
  await api(`/admin/orders/vendor-order-status/${vid}`, {
    method: 'PATCH',
    body: { status: newStatus },
  })
  const v = order.value.vendors.find(v => v.vid === vid)
  if (v) v.status = newStatus as any
  await refresh()
}

function calculateOrderTotal(): number {
  if (!order.value || !order.value.items) return 0
  return order.value.items.reduce((sum, item) => sum + (Number(item.unit_price) * item.quantity), 0)
}
</script>

<template>
  <div class="mx-auto max-w-5xl">
    <div class="flex items-center gap-3">
      <NuxtLink
        to="/admin/orders"
        class="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-teal-700 transition"
      >
        ← Back to Orders
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="mt-6 space-y-4">
      <div class="h-10 w-48 animate-pulse rounded-lg bg-slate-200" />
      <div class="h-48 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Error -->
    <div v-else-if="error || !order" class="mt-6 rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black text-slate-900">Order Not Found</h2>
      <p class="mt-1 text-sm text-slate-500">The requested order standard could not be loaded.</p>
      <NuxtLink to="/admin/orders" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2 text-xs font-bold text-white">
        Return to Orders
      </NuxtLink>
    </div>

    <!-- Details -->
    <div v-else class="mt-6 space-y-6">
      <!-- Order Header Card -->
      <div class="rounded-3xl bg-slate-950 p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-black uppercase tracking-widest text-teal-400">Order Record</p>
          <h1 class="mt-1 text-3xl font-black">#{{ order.order_number }}</h1>
          <p class="mt-1 text-xs text-slate-400">
            Placed on {{ new Date(order.created_at).toLocaleString() }}
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <span
            class="rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="order.paid ? 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/50' : 'bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/50'"
          >
            {{ order.paid ? 'Payment Paid' : 'Payment Unpaid' }}
          </span>
          <select
            class="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-bold capitalize text-white outline-none focus:border-teal-500"
            :value="order.status"
            @change="updateOrderStatus(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="s in orderStatusOptions" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="grid gap-6 md:grid-cols-2">
        <!-- Customer Details -->
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Customer Info</p>
          <h2 class="mt-1 text-lg font-black text-slate-900">{{ order.user?.fullname || 'Guest Customer' }}</h2>
          <p class="mt-1 text-sm text-slate-600">{{ order.user?.email }}</p>
          <div class="mt-3 flex items-center gap-2">
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold capitalize text-slate-700">
              Role: {{ order.user?.role }}
            </span>
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold capitalize text-slate-700">
              Status: {{ order.user?.status }}
            </span>
          </div>
        </div>

        <!-- Delivery Address -->
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Delivery Address</p>
          <div v-if="order.delivery_address" class="mt-2 text-sm text-slate-700 space-y-0.5">
            <p class="font-bold text-slate-900">{{ order.delivery_address.line_1 }}</p>
            <p v-if="order.delivery_address.line_2">{{ order.delivery_address.line_2 }}</p>
            <p>{{ order.delivery_address.city }}, {{ order.delivery_address.state }} {{ order.delivery_address.zip_code }}</p>
            <p v-if="order.delivery_address.landmark" class="text-xs text-slate-500">Landmark: {{ order.delivery_address.landmark }}</p>
          </div>
          <p v-else class="mt-2 text-sm text-slate-400">No address information.</p>
        </div>
      </div>

      <!-- Items List -->
      <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <h2 class="text-lg font-black text-slate-900">Order Items</h2>
          <p class="text-sm font-bold text-slate-500">{{ order.items?.length || 0 }} items</p>
        </div>

        <div class="divide-y divide-slate-100">
          <div
            v-for="(item, idx) in order.items"
            :key="idx"
            class="flex items-center justify-between gap-4 py-4"
          >
            <div class="flex items-center gap-4">
              <img
                v-if="item.product?.images?.[0]?.src"
                :src="item.product.images[0].src"
                :alt="item.product.name"
                class="h-14 w-14 rounded-xl object-cover ring-1 ring-slate-200"
              />
              <div v-else class="h-14 w-14 rounded-xl bg-slate-100 flex items-center justify-center text-xs text-slate-400">
                No Img
              </div>
              <div>
                <NuxtLink
                  :to="`/products/${item.product?.slug}`"
                  class="font-black text-slate-900 hover:text-teal-700 transition text-sm"
                >
                  {{ item.product?.name }}
                </NuxtLink>
                <p class="text-xs text-slate-500 mt-0.5">Quantity: {{ item.quantity }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-black text-slate-900 text-sm">{{ toUSD(Number(item.unit_price)) }}</p>
              <p class="text-xs text-slate-400">Subtotal: {{ toUSD(Number(item.unit_price) * item.quantity) }}</p>
            </div>
          </div>
        </div>

        <div class="mt-4 flex justify-between border-t border-slate-100 pt-4">
          <span class="font-black text-slate-900">Total Order Amount</span>
          <span class="text-xl font-black text-teal-700">{{ toUSD(calculateOrderTotal()) }}</span>
        </div>
      </div>

      <!-- Vendor Orders Breakdown -->
      <div v-if="order.vendors && order.vendors.length" class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 class="text-lg font-black text-slate-900">Vendor Sub-Orders</h2>
        <p class="text-xs text-slate-500 mt-0.5">Vendor payouts and status fulfillment records.</p>

        <div class="mt-4 space-y-4">
          <div
            v-for="vendor in order.vendors"
            :key="vendor.vid"
            class="rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200 flex flex-wrap items-center justify-between gap-3"
          >
            <div>
              <p class="font-black text-slate-900 text-sm">{{ vendor.store?.name }}</p>
              <p class="text-xs text-slate-500">{{ vendor.store?.email }} · {{ vendor.store?.city }}</p>
              <p class="mt-1 text-xs font-bold text-slate-700">Subtotal: {{ toUSD(Number(vendor.subtotal)) }}</p>
            </div>
            <div class="flex items-center gap-3">
              <label class="text-xs font-bold text-slate-500">Payout Status:</label>
              <select
                class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold capitalize"
                :value="vendor.status"
                @change="updateVendorStatus(vendor.vid, ($event.target as HTMLSelectElement).value)"
              >
                <option v-for="vs in vendorStatusOptions" :key="vs" :value="vs">{{ vs }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
