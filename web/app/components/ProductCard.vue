<script setup lang="ts">
import type { Product } from '~/types/api'
defineProps<{ product: Product }>()
</script>
<template>
  <NuxtLink :to="`/products/${product.slug}`" class="group block overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200 transition hover:-translate-y-1 hover:shadow-md">
    <img :src="product.images[0]?.src" :alt="product.images[0]?.alt || product.name" class="aspect-square w-full object-cover" />
    <div class="p-4"><p class="text-xs font-medium text-teal-700">{{ product.category?.name }}</p><h3 class="mt-1 font-bold text-slate-900">{{ product.name }}</h3><p class="mt-2 font-extrabold text-slate-950">{{ formatNaira(product.price) }}</p></div>
  </NuxtLink>
</template>
