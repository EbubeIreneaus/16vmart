<script setup lang="ts">
import type { OrderMini } from '~/types/api'

definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()

const { data: orders, pending } = await useAsyncData('my-orders', () =>
  api<OrderMini[]>('/shopping/orders'),
  { default: () => [] }
)

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
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 py-10">
    <NuxtLink to="/account" class="text-sm font-semibold text-teal-700">← My account</NuxtLink>
    <h1 class="mt-5 text-4xl font-black">My orders</h1>

    <div v-if="pending" class="mt-8 space-y-4">
      <div v-for="i in 3" :key="i" class="h-20 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <div
      v-else-if="orders.length < 1"
      class="mt-8 rounded-2xl border border-dashed border-slate-300 p-10 text-center"
    >
      <h2 class="text-xl font-black">No orders yet</h2>
      <NuxtLink to="/products" class="mt-3 inline-block font-bold text-teal-700">Start shopping →</NuxtLink>
    </div>

    <div v-else class="mt-8 space-y-3">
      <NuxtLink
        v-for="order in orders"
        :key="order.order_number"
        :to="`/account/orders/${order.order_number}`"
        class="flex items-center justify-between rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:shadow-md"
      >
        <div>
          <p class="font-black">{{ order.order_number }}</p>
          <p class="mt-1 text-sm text-slate-500">
            {{ new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' }) }}
          </p>
        </div>
        <div class="text-right">
          <span
            class="rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="statusColor(order.status)"
          >
            {{ order.status }}
          </span>
          <p v-if="order.paid" class="mt-1 text-xs text-emerald-600 font-semibold">Paid</p>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
