<script setup lang="ts">
import type { OrderDetail } from '~/types/api'
import { formatNaira } from '~/lib/money'

definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()
const route = useRoute()
const orderNumber = route.params.order_number as string

const { data: order, error } = await useAsyncData(`order-${orderNumber}`, () =>
  api<OrderDetail>(`/shopping/order/${orderNumber}`)
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Order not found' })
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 py-10" v-if="order">
    <NuxtLink to="/account/orders" class="text-sm font-semibold text-teal-700">← My orders</NuxtLink>

    <div class="mt-5 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black">{{ order.order_number }}</h1>
        <p class="mt-1 text-sm text-slate-500">
          Placed {{ new Date(order.created_at).toLocaleDateString('en-US', { dateStyle: 'long' }) }}
        </p>
      </div>
      <span
        class="rounded-full px-4 py-1.5 text-sm font-bold capitalize"
        :class="{
          'bg-emerald-100 text-emerald-700': order.status === 'delivered',
          'bg-blue-100 text-blue-700': order.status === 'processing',
          'bg-amber-100 text-amber-700': order.status === 'pending',
          'bg-rose-100 text-rose-700': order.status === 'cancelled' || order.status === 'failed',
        }"
      >
        {{ order.status }}
      </span>
    </div>

    <!-- Items -->
    <section class="mt-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black">Order items</h2>
      <div class="mt-4 space-y-4">
        <div
          v-for="item in order.items"
          :key="item.product.slug"
          class="flex items-center gap-4 border-b border-slate-100 pb-4 last:border-0 last:pb-0"
        >
          <img
            :src="item.product.images[0]?.src"
            :alt="item.product.name"
            class="size-16 rounded-xl object-cover"
          />
          <div class="flex-1">
            <p class="font-bold">{{ item.product.name }}</p>
            <p class="text-sm text-slate-500">Qty: {{ item.quantity }} × {{ formatNaira(item.unit_price) }}</p>
          </div>
          <p class="font-black">{{ formatNaira(Number(item.unit_price) * item.quantity) }}</p>
        </div>
      </div>
    </section>

    <!-- Delivery address -->
    <section class="mt-5 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black">Delivery address</h2>
      <div class="mt-3 text-sm text-slate-600">
        <p class="font-semibold text-slate-900">{{ order.delivery_address.line_1 }}</p>
        <p v-if="order.delivery_address.line_2">{{ order.delivery_address.line_2 }}</p>
        <p>{{ order.delivery_address.city }}, {{ order.delivery_address.state }} · {{ order.delivery_address.zip_code }}</p>
        <p v-if="order.delivery_address.landmark">Landmark: {{ order.delivery_address.landmark }}</p>
      </div>
    </section>
  </div>
</template>
