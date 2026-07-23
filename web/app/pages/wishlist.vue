<script setup lang="ts">
import type { WishlistOut, Page } from '~/types/api'
import { formatNaira } from '~/lib/money'

definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()
const wishlist = useWishlistStore()
const currentPage = ref(1)
const pageSize = 12

const { data: response, pending, refresh } = await useAsyncData(
  'wishlist-page',
  () => api<Page<WishlistOut>>(`/wishlists`, {
    params: { page: currentPage.value, size: pageSize },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: pageSize, pages: 1 }),
    watch: [currentPage],
  }
)

async function removeFromWishlist(slug: string) {
  await wishlist.remove(slug)
  await refresh()
}

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 py-10">
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Your collection</p>
    <h1 class="mt-2 text-4xl font-black">Wishlist</h1>

    <div v-if="pending" class="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
      <div v-for="i in 8" :key="i" class="aspect-square animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <div
      v-else-if="response.items.length < 1"
      class="mt-8 rounded-2xl border border-dashed border-slate-300 p-10 text-center"
    >
      <h2 class="text-xl font-black">Your wishlist is empty</h2>
      <p class="mt-2 text-slate-500">Save products you love to find them later.</p>
      <NuxtLink to="/products" class="mt-5 inline-block rounded-xl bg-teal-700 px-5 py-3 font-bold text-white">
        Browse products
      </NuxtLink>
    </div>

    <div v-else class="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
      <div
        v-for="item in response.items"
        :key="item.product.slug"
        class="group relative overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200"
      >
        <NuxtLink :to="`/products/${item.product.slug}`">
          <img
            :src="item.product.images[0]?.src"
            :alt="item.product.name"
            class="aspect-square w-full object-cover"
          />
          <div class="p-4">
            <h3 class="font-bold text-slate-900">{{ item.product.name }}</h3>
            <p class="mt-1 font-extrabold text-slate-950">{{ formatNaira(item.product.price) }}</p>
          </div>
        </NuxtLink>
        <button
          class="absolute right-3 top-3 rounded-full bg-white/90 p-2 text-rose-600 shadow-sm backdrop-blur"
          @click="removeFromWishlist(item.product.slug)"
          title="Remove from wishlist"
        >
          ♥
        </button>
      </div>
    </div>

    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
