<script setup lang="ts">
import type { OrderMini, Page } from '~/types/api'
import { formatNaira } from '~/lib/money'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const currentPage = ref(1)

const { data: response, pending, refresh } = await useAsyncData(
  'admin-orders',
  () => api<Page<OrderMini>>('/admin/orders/', {
    params: { page: currentPage.value, size: 20 },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage],
  }
)

const statusOptions = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', 'failed']

async function updateStatus(orderNumber: string, status: string) {
  await api(`/admin/orders/status/${orderNumber}`, {
    method: 'PATCH',
    body: { status },
  })
  await refresh()
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    pending: 'bg-amber-100 text-amber-700',
    processing: 'bg-blue-100 text-blue-700',
    shipped: 'bg-indigo-100 text-indigo-700',
    delivered: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-slate-100 text-slate-600',
    refunded: 'bg-purple-100 text-purple-700',
    failed: 'bg-rose-100 text-rose-700',
  }
  return map[status] || 'bg-slate-100 text-slate-600'
}

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Platform oversight</p>
    <h1 class="mt-2 text-4xl font-black">Orders</h1>

    <div v-if="pending" class="mt-7 space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <div v-else class="mt-7 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div
        v-for="order in response.items"
        :key="order.order_number"
        class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 py-4 last:border-0"
      >
        <div>
          <p class="font-black">{{ order.order_number }}</p>
          <p class="text-sm text-slate-500">
            Placed {{ new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' }) }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="order.paid" class="text-xs font-bold text-emerald-600">Paid</span>
          <select
            class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-bold capitalize"
            :value="order.status"
            @change="updateStatus(order.order_number, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>
      <div v-if="response.items.length < 1" class="py-8 text-center text-slate-500">
        No orders found.
      </div>
    </div>

    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
