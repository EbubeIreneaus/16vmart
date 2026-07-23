<script setup lang="ts">
import type { ProductDetail } from '~/types/api'
import { formatNaira } from '~/lib/money'

const config = useRuntimeConfig()
const route = useRoute()
const slug = route.params.slug as string

const cart = useCartStore()
const wishlist = useWishlistStore()
const addingToCart = ref(false)
const togglingWishlist = ref(false)
const addedToCart = ref(false)

const { data: product, error } = await useAsyncData(`product-${slug}`, () =>
  $fetch<ProductDetail>(`${config.public.apiUrl}/products/${slug}`)
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Product not found' })
}

async function handleAddToCart() {
  if (!product.value) return
  addingToCart.value = true
  try {
    await cart.addItem(product.value.slug)
    addedToCart.value = true
    setTimeout(() => (addedToCart.value = false), 2000)
  } finally {
    addingToCart.value = false
  }
}

async function handleToggleWishlist() {
  if (!product.value) return
  togglingWishlist.value = true
  try {
    await wishlist.toggle(product.value.slug)
  } finally {
    togglingWishlist.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 py-10" v-if="product">
    <NuxtLink to="/products" class="text-sm font-semibold text-teal-700">← Back to products</NuxtLink>

    <div class="mt-5 grid gap-8 md:grid-cols-2">
      <!-- Images -->
      <div>
        <img
          :src="product.images[0]?.src"
          :alt="product.name"
          class="aspect-square w-full rounded-2xl object-cover"
        />
        <div v-if="product.images.length > 1" class="mt-3 grid grid-cols-4 gap-2">
          <img
            v-for="(img, i) in product.images.slice(1, 5)"
            :key="i"
            :src="img.src"
            :alt="img.alt || product.name"
            class="aspect-square rounded-xl object-cover"
          />
        </div>
      </div>

      <!-- Details -->
      <div>
        <p class="font-semibold text-teal-700">{{ product.category?.name }}</p>
        <h1 class="mt-2 text-4xl font-black">{{ product.name }}</h1>
        <p class="mt-5 text-3xl font-black">{{ formatNaira(product.price) }}</p>

        <div v-if="product.condition" class="mt-3">
          <span
            class="rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="product.condition === 'brand new' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
          >
            {{ product.condition }}
          </span>
        </div>

        <p class="mt-6 leading-7 text-slate-600">{{ product.description }}</p>

        <!-- Attributes -->
        <div v-if="product.attributes?.length" class="mt-6 space-y-2">
          <h3 class="text-sm font-bold uppercase tracking-widest text-slate-500">Specifications</h3>
          <div
            v-for="attr in product.attributes"
            :key="attr.name"
            class="flex items-center justify-between border-b border-slate-100 py-2 text-sm"
          >
            <span class="font-semibold text-slate-600">{{ attr.name }}</span>
            <span class="text-slate-900">
              {{ Array.isArray(attr.value) ? attr.value.join(', ') : attr.value }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-8 flex gap-3">
          <button
            @click="handleAddToCart"
            :disabled="addingToCart"
            class="rounded-xl bg-teal-700 px-6 py-3 font-bold text-white disabled:opacity-60"
          >
            {{ addedToCart ? '✓ Added!' : addingToCart ? 'Adding…' : 'Add to cart' }}
          </button>
          <button
            @click="handleToggleWishlist"
            :disabled="togglingWishlist"
            class="rounded-xl border border-slate-300 px-4 py-3 font-bold disabled:opacity-60"
            :class="wishlist.isWishlisted(product.slug) ? 'bg-rose-50 border-rose-300 text-rose-700' : ''"
          >
            {{ wishlist.isWishlisted(product.slug) ? '♥ Saved' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
