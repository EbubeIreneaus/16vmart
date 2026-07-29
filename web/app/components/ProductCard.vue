<script setup lang="ts">
import { toUSD } from "~/lib/money"
import { toTitleCase } from "~/lib/text"
import type { ProductDetail } from "~/types/api"

const props = defineProps<{ product: ProductDetail }>()

const cart = useCartStore()
const wishlist = useWishlistStore()
const isAddingCart = ref(false)
const addedCart = ref(false)

async function handleAddToCart(e: Event) {
  e.preventDefault()
  e.stopPropagation()
  if (!props.product.slug) return
  isAddingCart.value = true
  try {
    await cart.addItem(props.product.slug)
    addedCart.value = true
    setTimeout(() => (addedCart.value = false), 2000)
  } finally {
    isAddingCart.value = false
  }
}

async function handleToggleWishlist(e: Event) {
  e.preventDefault()
  e.stopPropagation()
  if (!props.product.slug) return
  await wishlist.toggle(props.product.slug)
}
</script>

<template>
  <div class="group relative flex flex-col justify-between overflow-hidden rounded-2xl bg-white shadow-xs ring-1 ring-slate-200/80 transition duration-200 hover:-translate-y-1 hover:shadow-md">
    <NuxtLink :to="`/products/${product.slug}`" class="block">
      <div class="relative aspect-square w-full overflow-hidden bg-slate-100">
        <img
          :src="product.images?.[0]?.src"
          :alt="product.images?.[0]?.alt || product.name"
          class="h-full w-full object-cover group-hover:scale-105 transition duration-300"
        />

        <!-- Wishlist Button -->
        <button
          type="button"
          class="absolute top-3 right-3 rounded-full bg-white/90 p-2 shadow-xs backdrop-blur-xs hover:bg-white transition text-slate-400 hover:text-rose-600"
          :class="wishlist.isWishlisted(product.slug) ? 'text-rose-600' : ''"
          title="Save to Wishlist"
          @click="handleToggleWishlist"
        >
          <svg class="w-5 h-5" :fill="wishlist.isWishlisted(product.slug) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </button>
      </div>

      <div class="p-4">
        <p v-if="product.category?.name" class="text-xs font-bold uppercase tracking-wider text-teal-700">
          {{ toTitleCase(product.category.name) }}
        </p>
        <h3 class="mt-1 font-bold text-slate-900 line-clamp-2 text-sm group-hover:text-teal-700 transition">
          {{ toTitleCase(product.name) }}
        </h3>
        <p class="mt-2 font-black text-slate-950 text-base">
          {{ toUSD(product.price) }}
        </p>
      </div>
    </NuxtLink>

    <div class="px-4 pb-4">
      <button
        type="button"
        :disabled="isAddingCart"
        class="w-full rounded-xl bg-slate-900 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-teal-700 transition disabled:opacity-60 flex items-center justify-center gap-1.5"
        @click="handleAddToCart"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <span>{{ addedCart ? 'Added to Cart!' : isAddingCart ? 'Adding...' : 'Add to Cart' }}</span>
      </button>
    </div>
  </div>
</template>
