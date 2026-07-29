<script setup lang="ts">
import type { SingleProductOut } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const router = useRouter()
const storeSlug = String(route.params.store)
const slug = String(route.params.slug)
const { api } = useApi()

const { data: product, pending, error, refresh } = await useAsyncData(
  `vendor-single-product-${slug}`,
  () => api<SingleProductOut>(`/store/${storeSlug}/products/${slug}`)
)

const deleteModalOpen = ref(false)
const isDeleting = ref(false)

const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

async function deleteProduct() {
  if (!product.value) return
  clearErrors()
  isDeleting.value = true

  try {
    await api(`/store/${storeSlug}/products/${slug}`, {
      method: 'DELETE',
    })
    deleteModalOpen.value = false
    await router.push(`/vendor/${storeSlug}/products`)
  } catch (err) {
    setError(err)
  } finally {
    isDeleting.value = false
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <!-- Breadcrumb -->
    <div class="mb-6 flex items-center gap-2 text-sm text-slate-500">
      <NuxtLink :to="`/vendor/${storeSlug}/products`" class="hover:text-teal-700 font-medium transition flex items-center gap-1">
        &larr; Products
      </NuxtLink>
      <span>/</span>
      <span class="font-bold text-slate-800">{{ product ? toTitleCase(product.name) : slug }}</span>
    </div>

    <!-- Loading & Error -->
    <div v-if="pending" class="py-12 text-center text-slate-500">
      Loading product details...
    </div>

    <div v-else-if="error || !product" class="rounded-2xl bg-rose-50 p-8 text-center border border-rose-200">
      <h2 class="text-xl font-bold text-rose-800">Product not found</h2>
      <p class="mt-2 text-sm text-rose-600">The requested product could not be found or may have been deleted.</p>
      <NuxtLink :to="`/vendor/${storeSlug}/products`" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white">
        Return to Products
      </NuxtLink>
    </div>

    <div v-else class="space-y-8">
      <!-- Header & Actions -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-3xl font-black text-slate-900">{{ toTitleCase(product.name) }}</h1>
            <span
              class="rounded-full px-3 py-1 text-xs font-bold"
              :class="product.available ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
            >
              {{ product.available ? 'Live' : 'Unavailable' }}
            </span>
          </div>
          <p class="mt-1 text-xs font-mono text-slate-400">Slug: {{ product.slug }}</p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <NuxtLink
            :to="`/vendor/${storeSlug}/products/${slug}/edit`"
            class="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-slate-800 transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Product
          </NuxtLink>

          <NuxtLink
            :to="`/vendor/${storeSlug}/products/${slug}/images`"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 hover:bg-slate-50 transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Manage Images ({{ product.images?.length || 0 }})
          </NuxtLink>

          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200 px-4 py-2.5 text-sm font-bold text-rose-700 hover:bg-rose-100 transition"
            @click="deleteModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </div>

      <!-- Main Overview Grid -->
      <div class="grid gap-8 lg:grid-cols-3">
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview Card -->
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 class="text-lg font-black text-slate-900 border-b border-slate-100 pb-3">Price &amp; Overview</h2>

            <div class="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Price</p>
                <p class="mt-1 text-2xl font-black text-teal-700">{{ toUSD(product.price) }}</p>
              </div>
              <div>
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Condition</p>
                <p class="mt-1 font-bold text-slate-800 capitalize">{{ product.condition }}</p>
              </div>
            </div>

            <div class="mt-6 border-t border-slate-100 pt-4">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Description</p>
              <p class="mt-2 text-sm text-slate-700 leading-relaxed whitespace-pre-line">{{ product.description }}</p>
            </div>
          </div>

          <!-- Product Attributes Table -->
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 class="text-lg font-black text-slate-900">Product Attributes</h2>
              <span class="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full">
                {{ product.attributes?.length || 0 }} attributes
              </span>
            </div>

            <div v-if="product.attributes?.length" class="mt-4 divide-y divide-slate-100">
              <div v-for="attr in product.attributes" :key="attr.name" class="py-3 flex justify-between gap-4 text-sm">
                <span class="font-bold text-slate-800 capitalize">{{ attr.name }}</span>
                <span class="font-mono text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md text-xs">
                  {{ Array.isArray(attr.value) ? attr.value.join(', ') : attr.value }}
                </span>
              </div>
            </div>
            <p v-else class="mt-4 text-sm text-slate-400 italic">No attributes defined for this product.</p>
          </div>
        </div>

        <!-- Sidebar: Images Preview -->
        <div class="space-y-6">
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 class="text-lg font-black text-slate-900">Images</h2>
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${slug}/images`"
                class="text-xs font-bold text-teal-700 hover:underline"
              >
                Manage
              </NuxtLink>
            </div>

            <div v-if="product.images?.length" class="mt-4 grid grid-cols-2 gap-2">
              <img
                v-for="(img, idx) in product.images"
                :key="idx"
                :src="img.src"
                :alt="img.alt || product.name"
                class="h-28 w-full rounded-lg object-cover border border-slate-200"
              />
            </div>
            <div v-else class="mt-4 py-8 text-center text-sm text-slate-400 italic">
              No images uploaded yet.
              <NuxtLink
                :to="`/vendor/${storeSlug}/products/${slug}/images`"
                class="mt-3 block font-bold text-teal-700 hover:underline"
              >
                + Upload Images
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModalOpen" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="text-xl font-black text-slate-900">Delete Product</h3>
        <p class="mt-2 text-sm text-slate-600">
          Are you sure you want to delete <strong class="text-slate-900">{{ product?.name }}</strong>?
          This will mark the product as deleted and remove it from store listing.
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
