<script setup lang="ts">
import type { Category } from "~/types/api";
import { formatNaira } from "~/lib/money";

const config = useRuntimeConfig();
const auth = useAuthStore();
const cart = useCartStore();
const searchQuery = ref("");

const { data: categories } = await useAsyncData(
  "nav-categories",
  () => $fetch<Category[]>(`${config.public.apiUrl}/cat/all`),
  { default: () => [] },
);

function handleSearch() {
  if (searchQuery.value.trim().length >= 3) {
    navigateTo(`/products?q=${encodeURIComponent(searchQuery.value.trim())}`);
  }
}
</script>

<template>
  <div>
    <!-- Top banner -->
    <div
      class="bg-slate-950 px-5 py-2 text-center text-xs font-semibold text-slate-200"
    >
      Free delivery from selected stores on orders over $50
      <NuxtLink to="/seller" class="ml-2 text-teal-300"
        >Sell on 16Vmart →</NuxtLink
      >
    </div>

    <!-- Header -->
    <header
      class="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur"
    >
      <div
        class="mx-auto flex min-h-18 max-w-7xl flex-wrap items-center gap-4 px-5 py-3"
      >
        <AppLogo />

        <!-- Search bar -->
        <form
          class="order-3 flex w-full flex-1 rounded-xl border border-slate-200 bg-slate-50 p-1 md:order-none md:max-w-xl"
          @submit.prevent="handleSearch"
        >
          <input
            v-model="searchQuery"
            class="min-w-0 flex-1 bg-transparent px-3 text-sm outline-none"
            placeholder="Search products, brands and stores"
          />
          <button
            type="submit"
            class="rounded-lg bg-teal-700 px-4 py-2 text-sm font-bold text-white"
          >
            Search
          </button>
        </form>

        <!-- Right actions -->
        <div class="ml-auto flex items-center gap-4 text-sm font-semibold">
          <NuxtLink to="/categories" class="hidden lg:block"
            >Categories</NuxtLink
          >

          <!-- Wishlist -->
          <NuxtLink
            v-if="auth.isAuthenticated"
            to="/wishlist"
            class="hidden sm:block"
            title="Wishlist"
          >
            <Icon name="heroicons:heart" class="size-5" />
          </NuxtLink>

          <!-- Cart -->
          <NuxtLink to="/cart" class="relative" title="Cart">
            <Icon name="heroicons:shopping-bag" class="size-5" />
            <span
              v-if="cart.cartCount > 0"
              class="absolute -right-2 -top-2 grid size-5 place-items-center rounded-full bg-teal-700 text-[10px] font-black text-white"
            >
              {{ cart.cartCount > 99 ? "99+" : cart.cartCount }}
            </span>
          </NuxtLink>

          <!-- Auth state -->
          <template v-if="auth.isAuthenticated">
            <NuxtLink to="/vendor" class="hidden sm:block">My stores</NuxtLink>
            <UDropdownMenu
              :items="[
                [
                  { label: 'My account', to: '/account' },
                  { label: 'My orders', to: '/account/orders' },
                  { label: 'Wishlist', to: '/wishlist' },
                  { label: 'My stores', to: '/vendor' },
                ],
                [{ label: 'Sign out', to: '/auth/logout'}],
              ]"
            >
              <button
                class="grid size-9 place-items-center rounded-full bg-teal-100 text-sm font-black text-teal-800"
              >
                {{ auth.user?.fullname?.charAt(0)?.toUpperCase() || "?" }}
              </button>
            </UDropdownMenu>
          </template>
          <template v-else>
            <NuxtLink
              to="/auth/login"
              class="rounded-lg bg-slate-950 px-4 py-2 text-white"
            >
              Sign in
            </NuxtLink>
          </template>
        </div>
      </div>

      <!-- Category nav -->
      <nav
        class="mx-auto hidden max-w-7xl gap-7 px-5 pb-3 text-sm font-semibold text-slate-600 md:flex"
      >
        <NuxtLink to="/products">All products</NuxtLink>
        <NuxtLink
          v-for="category in (categories || []).slice(0, 6)"
          :key="category.slug"
          :to="`/products?category=${category.slug}`"
        >
          {{ category.name }}
        </NuxtLink>
        <NuxtLink to="/seller" class="text-teal-700">Open a store</NuxtLink>
      </nav>
    </header>

    <!-- Page content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="mt-12 bg-slate-950 px-5 py-12 text-slate-300">
      <div class="mx-auto grid max-w-7xl gap-8 md:grid-cols-[2fr_1fr_1fr_1fr]">
        <div>
          <AppLogo />
          <p class="mt-4 max-w-xs text-sm leading-6 text-slate-400">
            A considered marketplace for finding and growing independent
            businesses.
          </p>
        </div>
        <div>
          <p class="font-bold text-white">Shop</p>
          <NuxtLink to="/products" class="mt-3 block text-sm"
            >All products</NuxtLink
          >
          <NuxtLink to="/categories" class="mt-2 block text-sm"
            >Categories</NuxtLink
          >
        </div>
        <div>
          <p class="font-bold text-white">Sell</p>
          <NuxtLink to="/seller" class="mt-3 block text-sm"
            >Open a store</NuxtLink
          >
          <NuxtLink to="/vendor" class="mt-2 block text-sm"
            >Seller dashboard</NuxtLink
          >
        </div>
        <div>
          <p class="font-bold text-white">Help</p>
          <a class="mt-3 block text-sm" href="mailto:hello@16vmart.example"
            >Contact support</a
          >
          <p class="mt-2 text-sm">Terms & privacy</p>
        </div>
      </div>
      <p
        class="mx-auto mt-10 max-w-7xl border-t border-slate-800 pt-5 text-xs text-slate-500"
      >
        © 2026 16Vmart. Built for independent commerce.
      </p>
    </footer>
  </div>
</template>
