<script setup lang="ts">
import type { SingleProductOut } from '~/types/api'
import { toTitleCase } from '~/lib/text'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const router = useRouter()
const storeSlug = String(route.params.store)
const slug = String(route.params.slug)
const { api } = useApi()

const isSubmitting = ref(false)
const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Fetch existing product data
const { data: product, pending, error } = await useAsyncData(
  `vendor-edit-product-${slug}`,
  () => api<SingleProductOut>(`/store/${storeSlug}/products/${slug}`)
)

const form = reactive({
  name: '',
  price: 0,
  description: '',
  condition: 'brand new' as 'brand new' | 'used',
  available: true,
})

// Populate form when data is loaded
watch(product, (val) => {
  if (val) {
    form.name = val.name
    form.price = Number(val.price)
    form.description = val.description
    form.condition = val.condition
    form.available = val.available
  }
}, { immediate: true })

async function updateProduct() {
  clearErrors()
  isSubmitting.value = true

  try {
    await api(`/store/${storeSlug}/products/${slug}`, {
      method: 'PATCH',
      body: {
        name: form.name.trim(),
        price: form.price,
        description: form.description.trim(),
        condition: form.condition,
        available: form.available,
      },
    })
    await router.push(`/vendor/${storeSlug}/products/${slug}`)
  } catch (err) {
    setError(err)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-6">
    <!-- Breadcrumb -->
    <div class="mb-6 flex items-center gap-2 text-sm text-slate-500">
      <NuxtLink :to="`/vendor/${storeSlug}/products`" class="hover:text-teal-700 font-medium transition">
        Products
      </NuxtLink>
      <span>/</span>
      <NuxtLink :to="`/vendor/${storeSlug}/products/${slug}`" class="hover:text-teal-700 font-medium transition">
        {{ product ? toTitleCase(product.name) : slug }}
      </NuxtLink>
      <span>/</span>
      <span class="font-bold text-slate-800">Edit</span>
    </div>

    <!-- Loading & Error -->
    <div v-if="pending" class="py-12 text-center text-slate-500">
      Loading product details for editing...
    </div>

    <div v-else-if="error || !product" class="rounded-2xl bg-rose-50 p-8 text-center border border-rose-200">
      <h2 class="text-xl font-bold text-rose-800">Product not found</h2>
      <p class="mt-2 text-sm text-rose-600">The requested product could not be found or loaded.</p>
      <NuxtLink :to="`/vendor/${storeSlug}/products`" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white">
        Return to Products
      </NuxtLink>
    </div>

    <div v-else>
      <div class="border-b border-slate-200 pb-6">
        <h1 class="text-3xl font-black text-slate-900">Edit Product &mdash; {{ toTitleCase(product.name) }}</h1>
        <p class="mt-1 text-sm text-slate-500">Update pricing, description, condition, and availability.</p>
      </div>

      <form class="mt-8 space-y-6 rounded-2xl bg-white p-6 sm:p-8 shadow-sm ring-1 ring-slate-200" @submit.prevent="updateProduct">
        <p v-if="errorMessage" class="rounded-xl bg-rose-50 p-4 text-sm font-semibold text-rose-700 border border-rose-200">
          {{ errorMessage }}
        </p>

        <!-- Product Name -->
        <label class="block text-sm font-bold text-slate-800">
          Product Name <span class="text-rose-500">*</span>
          <input
            v-model="form.name"
            required
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
          />
        </label>

        <!-- Price & Condition -->
        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold text-slate-800">
            Price ($) <span class="text-rose-500">*</span>
            <input
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0"
              required
              class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
            />
          </label>

          <label class="text-sm font-bold text-slate-800">
            Condition
            <select v-model="form.condition" class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none">
              <option value="brand new">Brand New</option>
              <option value="used">Used</option>
            </select>
          </label>
        </div>

        <!-- Availability Switch -->
        <label class="text-sm font-bold text-slate-800 flex items-center gap-3">
          <input
            v-model="form.available"
            type="checkbox"
            class="h-5 w-5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
          />
          <span>Available for Sale in Store</span>
        </label>

        <!-- Product Description -->
        <label class="block text-sm font-bold text-slate-800">
          Description <span class="text-rose-500">*</span>
          <textarea
            v-model="form.description"
            required
            rows="5"
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
          />
        </label>

        <!-- Form Actions -->
        <div class="flex items-center justify-end gap-3 border-t border-slate-100 pt-6">
          <NuxtLink
            :to="`/vendor/${storeSlug}/products/${slug}`"
            class="rounded-xl border border-slate-300 px-5 py-2.5 text-sm font-bold text-slate-700 hover:bg-slate-100 transition"
          >
            Cancel
          </NuxtLink>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="rounded-xl bg-teal-700 px-6 py-2.5 text-sm font-bold text-white shadow-md hover:bg-teal-800 disabled:opacity-60 transition"
          >
            {{ isSubmitting ? 'Saving Changes...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
