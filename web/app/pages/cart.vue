<script setup lang="ts">
import { formatNaira } from '~/lib/money'

definePageMeta({ middleware: 'auth-required' })

const cart = useCartStore()
const loading = ref(true)

onMounted(async () => {
  await cart.fetchCart()
  loading.value = false
})

async function updateQty(slug: string, qty: number) {
  if (qty < 1) {
    await cart.removeItem(slug)
  } else {
    await cart.updateQuantity(slug, qty)
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 py-10">
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Shopping</p>
    <h1 class="mt-2 text-4xl font-black">Your cart</h1>

    <!-- Loading -->
    <div v-if="loading" class="mt-8 space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="cart.items.length < 1"
      class="mt-8 rounded-2xl border border-dashed border-slate-300 p-10 text-center"
    >
      <h2 class="text-xl font-black">Your cart is empty</h2>
      <p class="mt-2 text-slate-500">Start shopping to add items to your cart.</p>
      <NuxtLink to="/products" class="mt-5 inline-block rounded-xl bg-teal-700 px-5 py-3 font-bold text-white">
        Browse products
      </NuxtLink>
    </div>

    <!-- Cart items -->
    <div v-else class="mt-8 space-y-4">
      <div
        v-for="item in cart.items"
        :key="item.product.slug"
        class="flex items-center gap-5 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200"
      >
        <img
          :src="item.product.images[0]?.src"
          :alt="item.product.name"
          class="size-20 rounded-xl object-cover"
        />
        <div class="min-w-0 flex-1">
          <NuxtLink :to="`/products/${item.product.slug}`" class="font-bold text-slate-900 hover:text-teal-700">
            {{ item.product.name }}
          </NuxtLink>
          <p class="mt-1 text-sm font-extrabold text-slate-950">{{ formatNaira(item.product.price) }}</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="grid size-8 place-items-center rounded-lg border border-slate-300 text-lg font-bold"
            @click="updateQty(item.product.slug, item.quantity - 1)"
          >
            −
          </button>
          <span class="w-8 text-center font-bold">{{ item.quantity }}</span>
          <button
            class="grid size-8 place-items-center rounded-lg border border-slate-300 text-lg font-bold"
            @click="updateQty(item.product.slug, item.quantity + 1)"
          >
            +
          </button>
        </div>
        <button
          class="text-sm font-bold text-rose-600"
          @click="cart.removeItem(item.product.slug)"
        >
          Remove
        </button>
      </div>

      <!-- Summary -->
      <div class="rounded-2xl bg-slate-950 p-6 text-white">
        <div class="flex items-center justify-between text-lg">
          <span>Total ({{ cart.cartCount }} items)</span>
          <span class="text-2xl font-black">{{ formatNaira(cart.cartTotal) }}</span>
        </div>
        <NuxtLink
          to="/checkout"
          class="mt-5 block w-full rounded-xl bg-teal-500 py-3 text-center font-bold"
        >
          Proceed to checkout
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
