<script setup lang="ts">
definePageMeta({ middleware: 'auth-required' })

const auth = useAuthStore()

const links = [
  { label: 'My orders', to: '/account/orders', icon: 'heroicons:shopping-bag' },
  { label: 'My addresses', to: '/account/addresses', icon: 'heroicons:map-pin' },
  { label: 'Change password', to: '/account/change-password', icon: 'heroicons:lock-closed' },
  { label: 'My stores', to: '/vendor', icon: 'heroicons:building-storefront' },
]
</script>

<template>
  <div class="mx-auto max-w-3xl px-5 py-10">
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Account</p>
    <h1 class="mt-2 text-4xl font-black">My account</h1>

    <!-- Profile card -->
    <div class="mt-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div class="flex items-center gap-5">
        <div class="grid size-16 place-items-center rounded-full bg-teal-100 text-2xl font-black text-teal-800">
          {{ auth.user?.fullname?.charAt(0)?.toUpperCase() || '?' }}
        </div>
        <div>
          <h2 class="text-xl font-black">{{ auth.user?.fullname || 'User' }}</h2>
          <p class="text-sm text-slate-500">{{ auth.user?.email }}</p>
          <span class="mt-1 inline-block rounded-full bg-slate-100 px-3 py-0.5 text-xs font-bold capitalize text-slate-600">
            {{ auth.user?.role }}
          </span>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="mt-6 grid gap-3 md:grid-cols-2">
      <NuxtLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-4 rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-0.5 hover:shadow-md"
      >
        <Icon :name="link.icon" class="size-6 text-teal-700" />
        <span class="font-bold text-slate-900">{{ link.label }}</span>
        <span class="ml-auto text-slate-400">→</span>
      </NuxtLink>
    </div>

    <!-- Sign out -->
    <button
      class="mt-6 w-full rounded-xl border border-rose-300 py-3 font-bold text-rose-700"
      @click="auth.logout()"
    >
      Sign out
    </button>
  </div>
</template>
