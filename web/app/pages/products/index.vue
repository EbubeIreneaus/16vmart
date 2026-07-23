<script setup lang="ts">
import type { Product, Page, Category } from '~/types/api'
import { formatNaira } from '~/lib/money'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()

const query = ref(String(route.query.q || ''))
const parent = ref(String(route.query.category || ''))
const currentPage = ref(Number(route.query.page || 1))
const pageSize = 12

const { data: categories } = await useAsyncData('filter-categories', () =>
  $fetch<Category[]>(`${config.public.apiUrl}/cat/all`),
  { default: () => [] }
)

const { data: response, pending, refresh } = await useAsyncData(
  'products-list',
  async () => {
    // Determine which endpoint to hit
    if (query.value && query.value.trim().length >= 3) {
      return $fetch<Page<Product>>(`${config.public.apiUrl}/products/search`, {
        params: { s: query.value.trim(), page: currentPage.value, size: pageSize },
      })
    }
    if (parent.value) {
      return $fetch<Page<Product>>(`${config.public.apiUrl}/products/cat/${parent.value}`, {
        params: { page: currentPage.value, size: pageSize },
      })
    }
    return $fetch<Page<Product>>(`${config.public.apiUrl}/products/feature`, {
      params: { page: currentPage.value, size: pageSize },
    })
  },
  {
    default: () => ({ items: [], total: 0, page: 1, size: pageSize, pages: 1 }),
    watch: [currentPage],
  }
)

function apply() {
  currentPage.value = 1
  router.replace({
    query: {
      q: query.value || undefined,
      category: parent.value || undefined,
      page: undefined,
    },
  })
  refresh()
}

function clear() {
  query.value = ''
  parent.value = ''
  apply()
}

function changePage(page: number) {
  currentPage.value = page
  router.replace({ query: { ...route.query, page } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
  refresh()
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-5 py-10">
    <!-- Header -->
    <div class="rounded-2xl bg-slate-950 p-6 text-white md:p-8">
      <p class="text-sm font-bold uppercase tracking-widest text-teal-300">Marketplace</p>
      <h1 class="mt-2 text-4xl font-black">Browse products</h1>
      <form class="mt-6 flex max-w-3xl rounded-xl bg-white p-1" @submit.prevent="apply">
        <input
          v-model="query"
          class="min-w-0 flex-1 rounded-lg px-4 py-3 text-slate-900 outline-none"
          placeholder="What are you looking for?"
        />
        <button class="rounded-lg bg-teal-600 px-5 font-bold text-white">Search</button>
      </form>
    </div>

    <div class="mt-7 grid gap-8 lg:grid-cols-[280px_1fr]">
      <!-- Sidebar -->
      <aside class="h-fit rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 lg:sticky lg:top-28">
        <div class="flex items-center justify-between">
          <p class="font-black">Filters</p>
          <button class="text-sm font-bold text-teal-700" @click="clear">Clear all</button>
        </div>
        <label class="mt-5 block text-sm font-bold">
          Category
          <select
            v-model="parent"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            @change="apply()"
          >
            <option value="">All categories</option>
            <option v-for="category in categories" :key="category.slug" :value="category.slug">
              {{ category.name }}
            </option>
          </select>
        </label>
        <button
          class="mt-5 w-full rounded-lg border border-teal-700 py-3 text-sm font-bold text-teal-700"
          @click="apply"
        >
          Apply filters
        </button>
      </aside>

      <!-- Product grid -->
      <div>
        <div class="flex items-center justify-between">
          <p class="text-sm text-slate-500">
            <strong class="text-slate-900">{{ response.total }}</strong> products found
          </p>
        </div>

        <!-- Loading state -->
        <div v-if="pending" class="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="i in 8"
            :key="i"
            class="aspect-square animate-pulse rounded-2xl bg-slate-200"
          />
        </div>

        <!-- Products -->
        <div
          v-else-if="response.items.length"
          class="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4"
        >
          <ProductCard v-for="product in response.items" :key="product.slug" :product="product" />
        </div>

        <!-- Empty -->
        <div v-else class="mt-5 rounded-2xl border border-dashed border-slate-300 p-10 text-center">
          <h2 class="text-xl font-black">No products match those filters</h2>
          <button class="mt-3 font-bold text-teal-700" @click="clear">Clear filters</button>
        </div>

        <AppPagination :page="response" @change="changePage" />
      </div>
    </div>
  </div>
</template>
