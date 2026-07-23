<script setup lang="ts">
import { toUSD } from '~/lib/money'
import { toTitleCase } from '~/lib/text'

const cart = useCartStore()
const auth = useAuthStore()
const router = useRouter()

onMounted(async () => {
  await cart.fetchCart()
})

async function updateQty(slug: string, qty: number) {
  if (qty < 1) {
    await cart.removeItem(slug)
  } else {
    await cart.updateQuantity(slug, qty)
  }
}

function handleProceedToCheckout() {
  if (!auth.isAuthenticated) {
    router.push('/auth/login?redirect=/checkout')
  } else {
    router.push('/checkout')
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 py-10">
    <div class="flex items-center justify-between border-b border-slate-200 pb-4">
      <div>
        <p class="text-xs font-black uppercase tracking-widest text-teal-700">Shopping Cart</p>
        <h1 class="mt-1 text-3xl sm:text-4xl font-black text-slate-900">Your Cart</h1>
      </div>
      <NuxtLink to="/products" class="text-sm font-bold text-teal-700 hover:underline">
        &larr; Continue Shopping
      </NuxtLink>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="cart.loading" class="mt-8 space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Empty Cart State -->
    <div
      v-else-if="cart.items.length < 1"
      class="mt-8 rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center bg-white"
    >
      <div class="mx-auto w-16 h-16 rounded-full bg-teal-50 flex items-center justify-center text-teal-700 mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
        </svg>
      </div>
      <h2 class="text-2xl font-black text-slate-900">Your cart is empty</h2>
      <p class="mt-2 text-sm text-slate-500">Explore our catalog and add items to your cart.</p>
      <NuxtLink to="/products" class="mt-6 inline-block rounded-xl bg-teal-700 px-6 py-3 font-bold text-white shadow-md hover:bg-teal-800 transition">
        Browse Products
      </NuxtLink>
    </div>

    <!-- Cart Items List -->
    <div v-else class="mt-8 space-y-6">
      <div class="space-y-4">
        <div
          v-for="item in cart.items"
          :key="item.product.slug"
          class="flex items-center gap-5 rounded-2xl bg-white p-4 shadow-xs ring-1 ring-slate-200/80 hover:shadow-sm transition"
        >
          <img
            :src="item.product.images?.[0]?.src"
            :alt="item.product.name"
            class="size-20 rounded-xl object-cover border border-slate-100"
          />
          <div class="min-w-0 flex-1">
            <NuxtLink :to="`/products/${item.product.slug}`" class="font-bold text-slate-900 hover:text-teal-700 transition">
              {{ toTitleCase(item.product.name) }}
            </NuxtLink>
            <p class="mt-1 text-sm font-black text-teal-700">{{ toUSD(item.product.price) }}</p>
          </div>

          <!-- Quantity Controls -->
          <div class="flex items-center gap-2">
            <button
              class="grid size-8 place-items-center rounded-lg border border-slate-300 text-sm font-bold text-slate-700 hover:bg-slate-100 transition"
              @click="updateQty(item.product.slug, item.quantity - 1)"
            >
              &minus;
            </button>
            <span class="w-8 text-center font-bold text-sm text-slate-900">{{ item.quantity }}</span>
            <button
              class="grid size-8 place-items-center rounded-lg border border-slate-300 text-sm font-bold text-slate-700 hover:bg-slate-100 transition"
              @click="updateQty(item.product.slug, item.quantity + 1)"
            >
              +
            </button>
          </div>

          <button
            class="text-xs font-bold text-rose-600 hover:text-rose-800 transition"
            @click="cart.removeItem(item.product.slug)"
          >
            Remove
          </button>
        </div>
      </div>

      <!-- Cart Summary & Checkout Action -->
      <div class="rounded-2xl bg-slate-950 p-6 text-white shadow-xl">
        <div class="flex items-center justify-between text-base">
          <span class="text-slate-300">Total ({{ cart.cartCount }} item{{ cart.cartCount > 1 ? 's' : '' }})</span>
          <span class="text-2xl font-black text-teal-400">{{ toUSD(cart.cartTotal) }}</span>
        </div>

        <button
          type="button"
          class="mt-6 w-full rounded-xl bg-teal-500 py-3.5 text-center font-bold text-slate-950 shadow-md hover:bg-teal-400 transition"
          @click="handleProceedToCheckout"
        >
          Proceed to Checkout &rarr;
        </button>
        
        <p v-if="!auth.isAuthenticated" class="mt-2.5 text-center text-xs text-slate-400">
          You will be prompted to sign in or register before completing checkout.
        </p>
      </div>
    </div>
  </div>
</template>
