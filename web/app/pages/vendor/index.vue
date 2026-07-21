<script setup lang="ts">
import type { Store } from '~/types/api';

const cookie = useCookie("access_token")
const config = useRuntimeConfig()

const {data, error, refresh} = await useFetch<Store[]>(`${config.public.apiUrl}/store/entity`, {
  headers: {
    "Authorization": `Bearer ${cookie.value}`
  }
})

if (error.value){
  throw createError(error.value)
  
}

const stores: Store[] | undefined = data.value
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 py-10">
    <div class="flex flex-wrap items-end justify-between gap-5">
      <div>
        <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Seller workspace</p>
        <h1 class="mt-2 text-4xl font-black">My stores</h1>
        <p class="mt-2 text-slate-600">Choose a store to manage its catalogue, orders, payouts, and profile.</p>
      </div>
      <NuxtLink to="/vendor/create" class="rounded-xl bg-teal-700 px-5 py-3 font-bold text-white">+ Create a store
      </NuxtLink>
    </div>

    <div class="mt-8 grid gap-5 md:grid-cols-2" v-if="stores">
      <NuxtLink v-for="store in stores" :key="store.slug" :to="`/vendor/${store.slug}`"
        class="group rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-1 hover:shadow-md">
        <div class="flex items-start justify-between gap-4">
          <div class="grid size-12 place-items-center rounded-xl bg-teal-100 text-xl font-black text-teal-800">{{
            store.name.slice(0, 1) }}</div>
          <span class="rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="store.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">{{
              store.status.replace('_', ' ') }}</span>
        </div>
        <h2 class="mt-5 text-2xl font-black">{{ store.name }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ store.industry }} · {{ store.city }}, {{ store.state }}</p>
        <div class="mt-6 flex items-center justify-between border-t border-slate-100 pt-4 text-sm"><span
            class="text-slate-500">/{{ store.slug }}</span><span class="font-bold text-teal-700">Manage store →</span>
        </div>
      </NuxtLink>
      <NuxtLink to="/vendor/create"
        class="grid min-h-64 place-items-center rounded-2xl border-2 border-dashed border-slate-300 p-6 text-center transition hover:border-teal-500 hover:bg-teal-50">
        <div><span
            class="mx-auto grid size-12 place-items-center rounded-full bg-white text-2xl text-teal-700 shadow-sm">+</span>
          <h2 class="mt-4 text-xl font-black">Create another store</h2>
          <p class="mt-2 text-sm text-slate-500">Your account can own and manage multiple stores.</p>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
