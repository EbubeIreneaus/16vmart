<script setup lang="ts">
const route = useRoute()
const orderNumber = computed(() => (route.query.order_number as string) || '')
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-12">
    <div class="rounded-3xl bg-white p-8 sm:p-12 text-center shadow-xl ring-1 ring-slate-200/80 relative overflow-hidden">
      <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-amber-100 text-amber-600 shadow-xs">
        <svg class="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>

      <p class="mt-6 text-xs font-black uppercase tracking-widest text-amber-700">Checkout Cancelled</p>
      <h1 class="mt-1 text-3xl sm:text-4xl font-black text-slate-900">Payment Not Completed</h1>
      
      <p class="mt-3 text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
        Your payment session was cancelled or could not be completed. Your account has not been charged for this transaction.
      </p>

      <div v-if="orderNumber" class="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-100 px-4 py-2 text-xs font-mono font-bold text-slate-700">
        <span>Reference Order #:</span>
        <span class="text-slate-900 font-extrabold">{{ orderNumber }}</span>
      </div>

      <div class="mt-8 rounded-2xl bg-amber-50/70 p-5 border border-amber-200/80 max-w-lg mx-auto text-left text-xs text-amber-900 space-y-2">
        <p class="font-bold text-amber-950 text-sm">Need help completing your order?</p>
        <ul class="list-disc list-inside space-y-1 text-amber-800">
          <li>Your items are still saved in your shopping cart.</li>
          <li>Verify your card details, billing address, or try an alternative payment method.</li>
          <li>If you experienced a connection issue, simply click below to try again.</li>
        </ul>
      </div>

      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <NuxtLink
          to="/cart"
          class="rounded-xl bg-teal-700 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 transition"
        >
          Return to Cart &amp; Checkout
        </NuxtLink>
        <NuxtLink
          to="/products"
          class="rounded-xl border border-slate-300 px-6 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 transition"
        >
          Browse Products
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
