<script setup lang="ts">
import type { Product, Page, Category } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()

const query = ref(String(route.query.q || ''))
const parent = ref(String(route.query.category || ''))
const subCategory = ref(String(route.query.sub_category || ''))
const minPrice = ref(route.query.min_price ? String(route.query.min_price) : '')
const maxPrice = ref(route.query.max_price ? String(route.query.max_price) : '')
const condition = ref(String(route.query.condition || ''))
const currentPage = ref(Number(route.query.page || 1))
const pageSize = 12

// Fetch category taxonomy for filter sidebar
const { data: categories } = await useAsyncData('filter-categories', () =>
  $fetch<Category[]>(`${config.public.apiUrl}/cat/all`),
  { default: () => [] }
)

// Computed subcategories based on selected parent category
const selectedParentCategory = computed(() => {
  if (!parent.value) return null
  return categories.value.find(c => c.slug.toLowerCase() === parent.value.toLowerCase()) || null
})

const availableSubCategories = computed(() => {
  return selectedParentCategory.value?.sub_categories || []
})

// Reset subcategory if parent category changes and current subcategory is not valid
watch(parent, () => {
  if (subCategory.value) {
    const valid = availableSubCategories.value.some(s => s.slug.toLowerCase() === subCategory.value.toLowerCase())
    if (!valid) subCategory.value = ''
  }
})

const { data: response, pending, refresh } = await useAsyncData(
  'products-list',
  async () => {
    const targetCategory = subCategory.value || parent.value

    if (query.value && query.value.trim().length >= 3) {
      return $fetch<Page<Product>>(`${config.public.apiUrl}/products/search`, {
        params: { s: query.value.trim(), page: currentPage.value, size: pageSize },
      })
    }
    if (targetCategory) {
      return $fetch<Page<Product>>(`${config.public.apiUrl}/products/cat/${targetCategory}`, {
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
      sub_category: subCategory.value || undefined,
      min_price: minPrice.value || undefined,
      max_price: maxPrice.value || undefined,
      condition: condition.value || undefined,
      page: undefined,
    },
  })
  refresh()
}

function clear() {
  query.value = ''
  parent.value = ''
  subCategory.value = ''
  minPrice.value = ''
  maxPrice.value = ''
  condition.value = ''
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
    <!-- Header Banner -->
    <div class="rounded-3xl bg-slate-950 p-6 text-white md:p-8 shadow-xl">
      <p class="text-xs font-black uppercase tracking-widest text-teal-400">16vMart Catalog</p>
      <h1 class="mt-1 text-3xl sm:text-4xl font-black">Browse Products</h1>
      <form class="mt-6 flex max-w-3xl rounded-xl bg-white p-1 shadow-md" @submit.prevent="apply">
        <input
          v-model="query"
          class="min-w-0 flex-1 rounded-lg px-4 py-3 text-slate-900 outline-none text-sm"
          placeholder="Search products by title..."
        />
        <button class="rounded-lg bg-teal-600 px-6 font-bold text-white hover:bg-teal-700 transition text-sm">Search</button>
      </form>
    </div>

    <div class="mt-8 grid gap-8 lg:grid-cols-[280px_1fr]">
      <!-- Sidebar Filters Form -->
      <aside class="h-fit rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/80 lg:sticky lg:top-24 space-y-6">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <p class="font-black text-slate-900 text-base">Filter Catalog</p>
          <button type="button" class="text-xs font-bold text-teal-700 hover:underline" @click="clear">Clear All</button>
        </div>

        <!-- 1. Category Filter -->
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-500">
          Category
          <select
            v-model="parent"
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none capitalize text-slate-800"
            @change="apply()"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category.slug" :value="category.slug">
              {{ toTitleCase(category.name) }}
            </option>
          </select>
        </label>

        <!-- 2. Sub-Category Filter -->
        <label v-if="availableSubCategories.length" class="block text-xs font-bold uppercase tracking-wider text-slate-500">
          Sub-Category
          <select
            v-model="subCategory"
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none capitalize text-slate-800"
            @change="apply()"
          >
            <option value="">All Sub-categories</option>
            <option v-for="sub in availableSubCategories" :key="sub.slug" :value="sub.slug">
              {{ toTitleCase(sub.name) }}
            </option>
          </select>
        </label>

        <!-- 3. Price Range (Min & Max Price) -->
        <div class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Price Range ($)</p>
          <div class="grid grid-cols-2 gap-2">
            <input
              v-model="minPrice"
              type="number"
              min="0"
              step="0.01"
              placeholder="Min ($)"
              class="w-full rounded-xl border border-slate-300 p-2.5 text-sm focus:border-teal-600 outline-none"
            />
            <input
              v-model="maxPrice"
              type="number"
              min="0"
              step="0.01"
              placeholder="Max ($)"
              class="w-full rounded-xl border border-slate-300 p-2.5 text-sm focus:border-teal-600 outline-none"
            />
          </div>
        </div>

        <!-- 4. Condition / Status (Brand New or Used) -->
        <div class="space-y-2">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Condition / Status</p>
          <select
            v-model="condition"
            class="w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none text-slate-800 capitalize"
          >
            <option value="">All Conditions</option>
            <option value="brand new">Brand New</option>
            <option value="used">Used</option>
          </select>
        </div>

        <!-- Submit Filter Button -->
        <button
          type="button"
          class="w-full rounded-xl bg-teal-700 py-3 text-sm font-bold text-white shadow-xs hover:bg-teal-800 transition"
          @click="apply"
        >
          Apply Filters
        </button>
      </aside>

      <!-- Products Grid Display -->
      <div>
        <div class="flex items-center justify-between">
          <p class="text-sm text-slate-500">
            Showing <strong class="text-slate-900 font-black">{{ response.total }}</strong> products
          </p>
        </div>

        <!-- Loading State -->
        <div v-if="pending" class="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="i in 8"
            :key="i"
            class="aspect-square animate-pulse rounded-2xl bg-slate-200"
          />
        </div>

        <!-- Product Cards Grid -->
        <div
          v-else-if="response.items.length"
          class="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4"
        >
          <ProductCard v-for="product in response.items" :key="product.slug" :product="product as any" />
        </div>

        <!-- Empty Results -->
        <div v-else class="mt-5 rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center bg-white">
          <h2 class="text-xl font-black text-slate-900">No products found</h2>
          <p class="mt-1 text-sm text-slate-500">Try adjusting your filters or search terms.</p>
          <button type="button" class="mt-4 font-bold text-teal-700 text-sm hover:underline" @click="clear">Clear All Filters</button>
        </div>

        <AppPagination :page="response" @change="changePage" />
      </div>
    </div>
  </div>
</template>
