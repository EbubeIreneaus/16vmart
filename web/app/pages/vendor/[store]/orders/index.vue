<script setup lang="ts">
import type { VendorOrderMini, Page } from '~/types/api'
import { toUSD } from '~/lib/money'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const storeSlug = String(route.params.store)
const { api } = useApi()
const currentPage = ref(1)

const { data: response, pending, refresh } = await useAsyncData(
  `vendor-orders-${storeSlug}`,
  () => api<Page<VendorOrderMini>>(`/store/${storeSlug}/v-orders/`, {
    params: { page: currentPage.value, size: 20 },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage],
  }
)

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="border-b border-slate-200 pb-6">
      <p class="text-xs font-black uppercase tracking-widest text-teal-700">Sales &amp; Financials</p>
      <h1 class="mt-1 text-3xl font-black text-slate-900">Orders &amp; Payouts</h1>
      <p class="mt-1 text-sm text-slate-500">Track orders placed for your store products and payout statuses.</p>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="pending" class="mt-7 space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-xl bg-slate-200" />
    </div>

    <!-- Vendor Orders List -->
    <div v-else class="mt-7 rounded-2xl bg-white p-6 shadow-xs ring-1 ring-slate-200/80">
      <div
        v-for="order in response.items"
        :key="order.vid"
        class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 py-4 last:border-0 hover:bg-slate-50/50 p-3 rounded-xl transition"
      >
        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-slate-900 text-sm">Vendor Order</span>
            <span
              class="rounded-full px-2.5 py-0.5 text-xs font-bold capitalize"
              :class="order.status === 'paid' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
            >
              {{ order.status }}
            </span>
          </div>
          <p class="mt-1 text-xs font-mono text-slate-400">ID: {{ order.vid }}</p>
          <p class="mt-1 text-xs text-slate-500">
            Placed: {{ new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' }) }}
          </p>
        </div>

        <div class="flex items-center gap-6 text-right">
          <div>
            <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Store Items</p>
            <p class="mt-0.5 text-lg font-black text-teal-700">{{ toUSD(order.subtotal) }}</p>
          </div>

          <NuxtLink
            :to="`/vendor/${storeSlug}/orders/${order.vid}`"
            class="inline-flex items-center gap-1 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-teal-700 transition"
          >
            View Details &rarr;
          </NuxtLink>
        </div>
      </div>

      <div v-if="response.items.length < 1" class="py-12 text-center text-slate-500 text-sm">
        No orders recorded for your store yet.
      </div>
    </div>

    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
