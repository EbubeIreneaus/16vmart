<script setup lang="ts">
import type { Product, Page } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

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

const deleteModalOpen = ref(false)
const deletingProduct = ref<Product | null>(null)
const isDeleting = ref(false)

const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

function confirmDelete(product: Product) {
  deletingProduct.value = product
  deleteModalOpen.value = true
}

async function deleteProduct() {
  if (!deletingProduct.value) return
  clearErrors()
  isDeleting.value = true

  try {
    await api(`/store/${storeSlug}/products/${deletingProduct.value.slug}`, {
      method: 'DELETE',
    })
    deleteModalOpen.value = false
    deletingProduct.value = null
    await refresh()
  } catch (err) {
    setError(err)
  } finally {
    isDeleting.value = false
  }
}

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-end justify-between border-b border-slate-200 pb-6">
      <div>
        <p class="text-xs font-black uppercase tracking-widest text-teal-700">Catalog</p>
        <h1 class="mt-1 text-3xl font-black text-slate-900">Store Products</h1>
        <p class="mt-1 text-sm text-slate-500">Manage your product listings, pricing, images, and details.</p>
      </div>
      <NuxtLink
        :to="`/vendor/${storeSlug}/products/new`"
        class="inline-flex items-center gap-2 rounded-xl bg-teal-700 px-5 py-3 font-bold text-white shadow-md hover:bg-teal-800 transition"
      >
        + Add product
      </NuxtLink>
    </div>

    <div v-if="pending" class="mt-7 space-y-3">
      <div v-for="i in 5" :key="i" class="h-14 animate-pulse rounded-xl bg-slate-200" />
    </div>

    <div v-else class="mt-7 overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-50 text-slate-500 font-bold">
          <tr>
            <th class="p-4">Product Name</th>
            <th class="p-4">Price</th>
            <th class="p-4">Status</th>
            <th class="p-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="product in response.items" :key="product.slug" class="hover:bg-slate-50/50 transition">
            <td class="p-4">
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${product.slug}`"
                class="font-bold text-slate-900 hover:text-teal-700 transition"
              >
                {{ toTitleCase(product.name) }}
              </NuxtLink>
              <div class="text-xs font-mono text-slate-400 mt-0.5">{{ product.slug }}</div>
            </td>
            <td class="p-4 font-semibold text-slate-900">{{ toUSD(product.price) }}</td>
            <td class="p-4">
              <span
                class="rounded-full px-2.5 py-1 text-xs font-bold"
                :class="product.available ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
              >
                {{ product.available ? 'Live' : 'Unavailable' }}
              </span>
            </td>
            <td class="p-4 text-right space-x-3">
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${product.slug}`"
                class="font-bold text-slate-700 hover:text-teal-700 text-xs"
              >
                View
              </NuxtLink>
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${product.slug}/edit`"
                class="font-bold text-slate-700 hover:text-teal-700 text-xs"
              >
                Edit
              </NuxtLink>
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${product.slug}/images`"
                class="font-bold text-slate-700 hover:text-teal-700 text-xs"
              >
                Images
              </NuxtLink>
              <button
                type="button"
                class="font-bold text-rose-600 hover:text-rose-800 text-xs"
                @click="confirmDelete(product)"
              >
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="response.items.length < 1">
            <td colspan="4" class="p-8 text-center text-slate-500">No products yet. Add your first product above.</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <AppPagination :page="response" @change="changePage" />

    <!-- Delete Product Confirmation Modal -->
    <div v-if="deleteModalOpen" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="text-xl font-black text-slate-900">Delete Product</h3>
        <p class="mt-2 text-sm text-slate-600">
          Are you sure you want to delete <strong class="text-slate-900">{{ deletingProduct?.name }}</strong>?
          This action will remove the product from your store listing.
        </p>

        <p v-if="errorMessage" class="mt-4 rounded-xl bg-rose-50 p-3 text-xs font-semibold text-rose-700">
          {{ errorMessage }}
        </p>

        <div class="mt-6 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-bold text-slate-700 hover:bg-slate-100"
            @click="deleteModalOpen = false"
          >
            Cancel
          </button>
          <button
            type="button"
            :disabled="isDeleting"
            class="rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-60"
            @click="deleteProduct"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete Product' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
