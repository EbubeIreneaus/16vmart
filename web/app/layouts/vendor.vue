<script setup lang="ts">
const route = useRoute()
const store = useMockStore(String(route.params.store || 'northstar-goods'))
const links = [{ label: 'Overview', to: `/vendor/${store.value.slug}` }, { label: 'Products', to: `/vendor/${store.value.slug}/products` }, { label: 'Orders & payouts', to: `/vendor/${store.value.slug}/orders` }, { label: 'Store profile', to: `/vendor/${store.value.slug}/settings` }]
</script>
<template><div class="min-h-screen bg-slate-50 lg:flex"><aside class="w-full bg-slate-950 p-5 text-slate-300 lg:fixed lg:h-screen lg:w-64"><AppLogo /><p class="mt-8 text-xs font-semibold uppercase tracking-widest text-slate-500">{{ store.name }}</p><nav class="mt-3 flex gap-1 overflow-auto lg:block"><NuxtLink v-for="link in links" :key="link.to" :to="link.to" class="block whitespace-nowrap rounded-lg px-3 py-2.5 text-sm" :class="route.path === link.to ? 'bg-teal-500 text-white' : 'hover:bg-slate-800'">{{ link.label }}</NuxtLink></nav><NuxtLink to="/" class="mt-8 block text-sm text-slate-400">← Back to marketplace</NuxtLink></aside><main class="min-w-0 flex-1 lg:ml-64"><div class="mx-auto max-w-7xl p-5 md:p-9"><slot /></div></main></div></template>
