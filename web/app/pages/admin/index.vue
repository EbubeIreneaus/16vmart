<script setup lang="ts">
import type { Page, User, Store, OrderMini } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const auth = useAuthStore()

// Fetch metadata for admin dashboard
const { data: stats } = await useAsyncData(
  'admin-stats',
  () => api<{ users: number; stores: number; orders: number }>('/admin/metadata'),
  { default: () => ({ users: 0, stores: 0, orders: 0 }) }
)
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Platform control</p>
    <h1 class="mt-2 text-4xl font-black">Marketplace overview</h1>

    <div class="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="stat in [
          { l: 'Active users', v: stats.users.toLocaleString() },
          { l: 'Registered stores', v: stats.stores.toLocaleString() },
          { l: 'Total orders', v: stats.orders.toLocaleString() },
        ]"
        :key="stat.l"
        class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200"
      >
        <p class="text-sm text-slate-500">{{ stat.l }}</p>
        <p class="mt-2 text-3xl font-black">{{ stat.v }}</p>
      </div>
    </div>

    <section class="mt-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black">Role-aware administration</h2>
      <p class="mt-2 text-slate-600">
        This interface uses the current role to control sensitive actions. You are signed in as
        <strong class="capitalize">{{ auth.user?.role }}</strong>. Server-side authorization remains the
        source of truth.
      </p>
    </section>
  </div>
</template>
