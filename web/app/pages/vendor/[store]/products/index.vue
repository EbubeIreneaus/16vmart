<script setup lang="ts">
import type { Product, Page } from '~/types/api'
import { formatNaira } from '~/lib/money'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const storeSlug = String(route.params.store)
const { api } = useApi()
const currentPage = ref(1)

const { data: response, pending, refresh } = await useAsyncData(
  `vendor-products-${storeSlug}`,
  () => api<Page<Product>>(`/store/${storeSlug}/products/all`, {
    params: { page: currentPage.value, size: 20 },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage],
  }
)

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div>
    <div class="flex items-end justify-between">
      <div>
        <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Catalog</p>
        <h1 class="mt-2 text-4xl font-black">Products</h1>
      </div>
      <NuxtLink
        :to="`/vendor/${storeSlug}/products/new`"
        class="rounded-xl bg-teal-700 px-5 py-3 font-bold text-white"
      >
        + Add product
      </NuxtLink>
    </div>

    <div v-if="pending" class="mt-7 space-y-3">
      <div v-for="i in 5" :key="i" class="h-14 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <div v-else class="mt-7 overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-50 text-slate-500">
          <tr>
            <th class="p-4">Product</th>
            <th class="p-4">Price</th>
            <th class="p-4">Status</th>
            <th class="p-4"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in response.items" :key="product.slug" class="border-t border-slate-100">
            <td class="p-4 font-bold">{{ product.name }}</td>
            <td class="p-4">{{ formatNaira(product.price) }}</td>
            <td class="p-4">
              <span
                class="rounded-full px-2 py-1 text-xs font-bold"
                :class="product.available ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
              >
                {{ product.available ? 'Live' : 'Unavailable' }}
              </span>
            </td>
            <td class="p-4 text-right">
              <NuxtLink :to="`/products/${product.slug}`" class="font-bold text-teal-700">View</NuxtLink>
            </td>
          </tr>
          <tr v-if="response.items.length < 1">
            <td colspan="4" class="p-8 text-center text-slate-500">No products yet. Add your first product above.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
