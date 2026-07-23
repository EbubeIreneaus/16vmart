<script setup lang="ts">
import type { Product, Page, Category, ProductDetail } from '~/types/api'
import { formatNaira } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

const config = useRuntimeConfig()

const { data: categories } = await useAsyncData('all-categories', () =>
  $fetch<Category[]>(`${config.public.apiUrl}/cat/all`),
  { default: () => [] }
)

const { data: featured } = await useAsyncData('featured-products', () =>
  $fetch<Page<Product>>(`${config.public.apiUrl}/products/feature`, {
    params: { page: 1, size: 8 },
  }),
  { default: () => ({ items: [], total: 0, page: 1, size: 8, pages: 1 }) }
)

const { data: trending } = await useAsyncData('trending-products', () =>
  $fetch<Page<Product>>(`${config.public.apiUrl}/products/feature`, {
    params: { page: 2, size: 8 },
  }),
  { default: () => ({ items: [], total: 0, page: 1, size: 8, pages: 1 }) }
)
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="overflow-hidden bg-slate-950 px-5 py-14 text-white md:py-20">
      <div class="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-[1.05fr_.95fr]">
        <div>
          <p class="text-sm font-bold uppercase tracking-[.2em] text-teal-300">
            The marketplace for everyday life
          </p>
          <h1 class="mt-5 max-w-3xl text-4xl font-black tracking-tight md:text-6xl">
            Find what moves your world.
          </h1>
          <p class="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Shop original finds from independently owned stores, with one place to discover, compare and buy.
          </p>
          <NuxtLink
            to="/products"
            class="mt-8 inline-block rounded-xl bg-teal-500 px-6 py-3 font-bold text-white"
          >
            Explore the marketplace
          </NuxtLink>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <img
            v-for="product in featured.items.slice(0, 4)"
            :key="product.slug"
            :src="product.images[0]?.src"
            :alt="product.name"
            class="aspect-square rounded-2xl object-cover odd:translate-y-5"
          />
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="mx-auto max-w-7xl px-5 py-12">
      <div class="flex items-end justify-between">
        <div>
          <p class="text-sm font-semibold text-teal-700">SHOP BY DEPARTMENT</p>
          <h2 class="mt-1 text-3xl font-black">Start with what you need</h2>
        </div>
        <NuxtLink to="/categories" class="font-semibold text-teal-700">All categories →</NuxtLink>
      </div>
      <div class="mt-7 grid gap-4 sm:grid-cols-3">
        <NuxtLink
          v-for="category in categories.slice(6, 13)"
          :key="category.slug"
          :to="`/products?category=${category.slug}`"
          class="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:border-teal-500 hover:shadow-md"
        >
          <p class="text-xs font-bold uppercase tracking-widest text-teal-700">
            {{ category.sub_categories?.length || 0 }} departments
          </p>
          <h3 class="mt-2 text-2xl font-black">{{ toTitleCase(category.name) }}</h3>
          <p class="mt-4 text-sm text-slate-500">
            {{ category.sub_categories?.map((sub: Category) => toTitleCase(sub.name)).join(' · ') }}
          </p>
          <span class="mt-5 block font-bold text-slate-900">Shop category →</span>
        </NuxtLink>
      </div>
    </section>

    <!-- Featured -->
    <section class="bg-white py-12">
      <div class="mx-auto max-w-7xl px-5">
        <div class="flex items-end justify-between">
          <div>
            <p class="text-sm font-semibold text-teal-700">CURATED FOR YOU</p>
            <h2 class="mt-1 text-3xl font-black">Featured finds</h2>
          </div>
          <NuxtLink to="/products" class="font-semibold text-teal-700">View all →</NuxtLink>
        </div>
        <div class="mt-7 grid grid-cols-2 gap-4 md:grid-cols-4">
          <ProductCard v-for="product in featured.items" :key="product.slug" :product="product as ProductDetail" />
        </div>
      </div>
    </section>

    <!-- Seller CTA -->
    <section class="mx-auto max-w-7xl px-5 py-12">
      <div class="rounded-3xl bg-teal-700 p-8 text-white md:flex md:items-center md:justify-between">
        <div>
          <p class="text-sm font-bold uppercase tracking-widest text-teal-100">For independent sellers</p>
          <h2 class="mt-2 text-3xl font-black">Turn your inventory into a storefront.</h2>
          <p class="mt-3 max-w-xl text-teal-50">
            Manage multiple stores, catalogue products and follow each vendor order from one workspace.
          </p>
        </div>
        <NuxtLink
          to="/seller"
          class="mt-6 inline-block rounded-xl bg-white px-5 py-3 font-bold text-teal-800 md:mt-0"
        >
          Start selling
        </NuxtLink>
      </div>
    </section>

    <!-- Trending -->
    <section class="mx-auto max-w-7xl px-5 pb-4">
      <div class="flex items-end justify-between">
        <div>
          <p class="text-sm font-semibold text-teal-700">FRESH THIS WEEK</p>
          <h2 class="mt-1 text-3xl font-black">Trending now</h2>
        </div>
        <NuxtLink to="/products" class="font-semibold text-teal-700">Browse all →</NuxtLink>
      </div>
      <div class="mt-7 grid grid-cols-2 gap-4 md:grid-cols-4">
        <ProductCard v-for="product in trending.items" :key="product.slug" :product="product as ProductDetail" />
      </div>
    </section>
  </div>
</template>
