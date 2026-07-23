<script setup lang="ts">
import type { VendorOrderMini, Page } from '~/types/api'
import { formatNaira } from '~/lib/money'

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
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Sales</p>
    <h1 class="mt-2 text-4xl font-black">Orders & payouts</h1>

    <div v-if="pending" class="mt-7 space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <div v-else class="mt-7 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div
        v-for="order in response.items"
        :key="order.vid"
        class="flex items-center justify-between border-b border-slate-100 py-4 last:border-0"
      >
        <div>
          <p class="font-bold">Vendor order</p>
          <p class="mt-1 text-sm text-slate-500">{{ order.vid }}</p>
          <p class="mt-1 text-xs text-slate-400">
            {{ new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' }) }}
          </p>
        </div>
        <div class="text-right">
          <p class="font-black">{{ formatNaira(order.subtotal) }}</p>
          <span
            class="rounded-full px-2 py-0.5 text-xs font-bold capitalize"
            :class="order.status === 'paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
          >
            {{ order.status }}
          </span>
        </div>
      </div>
      <div v-if="response.items.length < 1" class="py-8 text-center text-slate-500">
        No orders yet.
      </div>
    </div>
    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
