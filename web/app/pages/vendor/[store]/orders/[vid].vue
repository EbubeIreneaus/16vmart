<script setup lang="ts">
import type { SingleVendorOrder } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const storeSlug = String(route.params.store)
const vid = String(route.params.vid)
const { api } = useApi()

const { data: order, pending, error } = await useAsyncData(
  `vendor-single-order-${vid}`,
  () => api<SingleVendorOrder>(`/store/${storeSlug}/v-orders/${vid}`)
)
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6 space-y-6">
    <!-- Breadcrumb & Back -->
    <div class="flex items-center gap-2 text-sm text-slate-500">
      <NuxtLink :to="`/vendor/${storeSlug}/orders`" class="hover:text-teal-700 font-bold transition flex items-center gap-1">
        &larr; Sales &amp; Orders
      </NuxtLink>
      <span>/</span>
      <span class="font-bold text-slate-800 font-mono text-xs">{{ vid }}</span>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="pending" class="py-12 text-center text-slate-500">
      Loading order details...
    </div>

    <!-- Error State -->
    <div v-else-if="error || !order" class="rounded-2xl bg-rose-50 p-8 text-center border border-rose-200">
      <h2 class="text-xl font-bold text-rose-800">Order Not Found</h2>
      <p class="mt-2 text-sm text-rose-600">The requested vendor order could not be loaded.</p>
      <NuxtLink :to="`/vendor/${storeSlug}/orders`" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white">
        Back to Orders
      </NuxtLink>
    </div>

    <!-- Single Order Content -->
    <div v-else class="space-y-6">
      <!-- Order Header Card -->
      <div class="rounded-2xl bg-white p-6 sm:p-8 shadow-xs ring-1 ring-slate-200/80 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl sm:text-3xl font-black text-slate-900">Vendor Order</h1>
            <span
              class="rounded-full px-3 py-1 text-xs font-bold capitalize"
              :class="order.status === 'paid' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
            >
              Payout: {{ order.status }}
            </span>
          </div>
          <p class="mt-1 text-xs font-mono text-slate-400">Order ID (VID): {{ order.vid }}</p>
          <p class="mt-1 text-xs text-slate-500">
            Placed on: {{ new Date(order.created_at).toLocaleString('en-US', { dateStyle: 'long', timeStyle: 'short' }) }}
          </p>
          <p v-if="order.paid_at" class="text-xs text-emerald-700 font-semibold mt-0.5">
            Paid on: {{ new Date(order.paid_at).toLocaleString('en-US', { dateStyle: 'long', timeStyle: 'short' }) }}
          </p>
        </div>

        <div class="text-right">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Store Earnings</p>
          <p class="mt-1 text-3xl font-black text-teal-700">{{ toUSD(order.subtotal) }}</p>
        </div>
      </div>

      <!-- Items Concerning Vendor's Store -->
      <div class="rounded-2xl bg-white p-6 sm:p-8 shadow-xs ring-1 ring-slate-200/80">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <h2 class="text-lg font-black text-slate-900">Items Ordered from Your Store</h2>
          <span class="text-xs font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-full">
            {{ order.items?.length || 0 }} item{{ (order.items?.length || 0) > 1 ? 's' : '' }}
          </span>
        </div>

        <div class="mt-4 overflow-hidden">
          <table class="w-full text-left text-sm">
            <thead class="bg-slate-50 text-slate-500 font-bold">
              <tr>
                <th class="p-4">Product Name</th>
                <th class="p-4 text-center">Quantity</th>
                <th class="p-4 text-right">Unit Price</th>
                <th class="p-4 text-right">Subtotal</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(item, idx) in order.items" :key="idx" class="hover:bg-slate-50/50 transition">
                <td class="p-4 font-bold text-slate-900">
                  {{ toTitleCase(item.product_name) }}
                </td>
                <td class="p-4 text-center font-semibold text-slate-700">
                  {{ item.quantity }}
                </td>
                <td class="p-4 text-right font-semibold text-slate-700">
                  {{ toUSD(item.unit_price) }}
                </td>
                <td class="p-4 text-right font-black text-teal-700">
                  {{ toUSD(Number(item.unit_price) * item.quantity) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
