<script setup lang="ts">
import type { Category } from '~/types/api'

const config = useRuntimeConfig()

const { data: categories } = await useAsyncData('categories-page', () =>
  $fetch<Category[]>(`${config.public.apiUrl}/cat/all`),
  { default: () => [] }
)
</script>

<template>
  <div class="mx-auto max-w-7xl px-5 py-10">
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Shop by category</p>
    <h1 class="mt-2 text-4xl font-black">Everything has a place.</h1>
    <div class="mt-8 grid gap-5 md:grid-cols-3">
      <section
        v-for="category in categories"
        :key="category.slug"
        class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      >
        <h2 class="text-xl font-black">{{ category.name }}</h2>
        <div class="mt-4 space-y-2">
          <NuxtLink
            v-for="sub in category.sub_categories"
            :key="sub.slug"
            :to="`/products?category=${sub.slug}`"
            class="block text-slate-600 hover:text-teal-700"
          >
            {{ sub.name }} <span class="float-right">→</span>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>
