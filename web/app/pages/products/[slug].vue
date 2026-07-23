<script setup lang="ts">
import type { ProductDetail } from '~/types/api'
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()
const slug = route.params.slug as string

const cart = useCartStore()
const wishlist = useWishlistStore()
const auth = useAuthStore()

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
    setTimeout(() => (addedToCart.value = false), 2500)
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

function handleBuyNow() {
  if (!product.value) return
  cart.addItem(product.value.slug)
  if (!auth.isAuthenticated) {
    router.push('/auth/login?redirect=/checkout')
  } else {
    router.push('/checkout')
  }
}
</script>

<template>
  <div class="mx-auto max-w-6xl px-5 py-10" v-if="product">
    <NuxtLink to="/products" class="text-sm font-bold text-teal-700 hover:underline flex items-center gap-1">
      &larr; Back to Products
    </NuxtLink>

    <div class="mt-6 grid gap-10 md:grid-cols-2">
      <!-- Images Gallery -->
      <div>
        <div class="aspect-square w-full overflow-hidden rounded-2xl bg-slate-100 border border-slate-200 shadow-xs">
          <img
            :src="product.images[0]?.src"
            :alt="product.name"
            class="h-full w-full object-cover"
          />
        </div>
        <div v-if="product.images.length > 1" class="mt-4 grid grid-cols-4 gap-3">
          <img
            v-for="(img, i) in product.images.slice(1, 5)"
            :key="i"
            :src="img.src"
            :alt="img.alt || product.name"
            class="aspect-square rounded-xl object-cover border border-slate-200 cursor-pointer hover:opacity-80 transition"
          />
        </div>
      </div>

      <!-- Product Details & Buying Actions -->
      <div>
        <p v-if="product.category?.name" class="text-xs font-bold uppercase tracking-widest text-teal-700">
          {{ toTitleCase(product.category.name) }}
        </p>

        <h1 class="mt-2 text-3xl sm:text-4xl font-black text-slate-900">
          {{ toTitleCase(product.name) }}
        </h1>

        <p class="mt-4 text-3xl font-black text-slate-950">
          {{ toUSD(product.price) }}
        </p>

        <div v-if="product.condition" class="mt-3">
          <span
            class="inline-block rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="product.condition === 'brand new' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
          >
            {{ product.condition }}
          </span>
        </div>

        <p class="mt-6 leading-relaxed text-slate-600 text-sm whitespace-pre-line">
          {{ product.description }}
        </p>

        <!-- Specifications / Attributes -->
        <div v-if="product.attributes?.length" class="mt-8 rounded-2xl bg-slate-50/70 p-5 border border-slate-200/80">
          <h3 class="text-xs font-black uppercase tracking-wider text-slate-500 pb-2 border-b border-slate-200">
            Specifications
          </h3>
          <div class="mt-2 divide-y divide-slate-200/60">
            <div
              v-for="attr in product.attributes"
              :key="attr.name"
              class="flex items-center justify-between py-2 text-sm"
            >
              <span class="font-bold text-slate-700 capitalize">{{ attr.name }}</span>
              <span class="text-slate-900 font-medium">
                {{ Array.isArray(attr.value) ? attr.value.join(', ') : attr.value }}
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-8 space-y-3">
          <div class="flex gap-3">
            <button
              @click="handleAddToCart"
              :disabled="addingToCart"
              class="flex-1 rounded-xl bg-teal-700 px-6 py-3.5 font-bold text-white shadow-md hover:bg-teal-800 transition disabled:opacity-60 flex items-center justify-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>{{ addedToCart ? '✓ Added to Cart!' : addingToCart ? 'Adding...' : 'Add to Cart' }}</span>
            </button>

            <button
              @click="handleToggleWishlist"
              :disabled="togglingWishlist"
              class="rounded-xl border border-slate-300 px-5 py-3.5 font-bold transition disabled:opacity-60 flex items-center gap-2"
              :class="wishlist.isWishlisted(product.slug) ? 'bg-rose-50 border-rose-300 text-rose-700' : 'bg-white text-slate-700 hover:bg-slate-50'"
            >
              <svg class="w-5 h-5" :fill="wishlist.isWishlisted(product.slug) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <span>{{ wishlist.isWishlisted(product.slug) ? 'Saved' : 'Save' }}</span>
            </button>
          </div>

          <button
            @click="handleBuyNow"
            class="w-full rounded-xl bg-slate-900 py-3.5 font-bold text-white shadow-md hover:bg-slate-800 transition text-center"
          >
            Buy Now (Checkout) &rarr;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
