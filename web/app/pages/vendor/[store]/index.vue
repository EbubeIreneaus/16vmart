<script setup lang="ts">
import { toUSD } from "~/lib/money";
import type { Store } from "~/types/api";

const route = useRoute();
definePageMeta({ layout: "vendor" });
const config = useRuntimeConfig();
const cookie = useCookie("access_token");
const store_slug = useRoute().params.store;

const { data, error, refresh } = await useAsyncData("store-home", async () => {
  const headers = {
    Authorization: `Bearer ${cookie.value}`,
  };
  const [metadata, store] = await Promise.allSettled([
    $fetch<{
      live_products: number;
      monthly_orders: number;
      pending_payout: number;
    }>(`${config.public.apiUrl}/store/${store_slug}/metadata`, { headers }),
    $fetch<Store>(`${config.public.apiUrl}/store/entity/${store_slug}`, {
      headers,
    }),
  ]);

  const unauthorized =
    (metadata.status === "rejected" && metadata.reason?.statusCode === 401) ||
    (store.status === "rejected" && store.reason?.statusCode === 401);

  const notFound =
    (metadata.status === "rejected" && metadata.reason?.statusCode === 404) ||
    (store.status === "rejected" && store.reason?.statusCode === 404);

  if (notFound) {
    throw createError({ statusCode: 404, statusMessage: "Store not found" });
  }
  if (unauthorized) {
    throw createError({
      statusCode: 401,
      statusMessage:
        "Unauthorized, this might be because your session has expired, try logging in again",
    });
  }

  return {
    metadata: metadata.status == "fulfilled" ? metadata.value : null,
    store: store.status == "fulfilled" ? store.value : null,
    error: {
      metadata: metadata.status == "rejected" ? metadata.reason.detail : null,

    },
  };
});

if (error.value) {
  if (error.value.status == 401) {
    cookie.value = null;
    await navigateTo("/auth/login");
  } else {
    throw createError(error.value);
  }
}
const store_data = data.value?.metadata;
const store = data.value?.store;
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">
      Store dashboard
    </p>
    <div class="mt-2 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-4xl font-black">Good morning, {{ store?.name }}.</h1>
        <p class="mt-2 text-slate-500">
          Here is today metrics.
        </p>
      </div>
      <NuxtLink
        :to="`/vendor/${store_slug}/products/new`"
        class="rounded-xl bg-teal-700 px-5 py-3 font-bold text-white"
        >+ Add product</NuxtLink
      >
    </div>
    <div class="mt-8 grid gap-4 sm:grid-cols-3">
      <div
        v-for="stat in [
          { l: 'Products live', v: store_data?.live_products },
          { l: 'Orders this month', v: store_data?.monthly_orders },
          { l: 'Pending payout', v: toUSD(store_data?.pending_payout) },
        ]"
        :key="stat.l"
        class="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200"
      >
        <p class="text-sm text-slate-500">{{ stat.l }}</p>
        <p class="mt-2 text-3xl font-black">{{ stat.v }}</p>
      </div>
    </div>
    <section
      class="mt-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
    >
      <div class="flex justify-between">
        <h2 class="text-xl font-black">Store status</h2>
        <span
          :class="{
            'bg-emerald-100 text-emerald-700': store?.status == 'active',
            'bg-yellow-100 text-yellow-700': store?.status == 'under_review',
            'bg-red-100 text-red-700': store?.status != 'active',
          }"
          class="rounded-full px-3 py-1 text-sm font-bold text-emerald-700"
          >{{ store?.status.replace("_", " ").toUpperCase()}}</span
        >
      </div>
      <p class="mt-3 text-slate-600" v-if="store?.status == 'active'">
        Your store is visible to customers and ready to receive orders.
      </p>
      <p v-else-if="store?.status == 'under_review'">
        Your store is under review, it will be visible to customers once approved.
      </p>
      <p v-else-if="store?.status == 'suspended'">
        Your store is suspended, please contact support for assistance.
      </p>
      <p v-else-if="store?.status == 'terminated'">
        Your store is terminated, please contact support for assistance.
      </p>
      <p v-else-if="store?.status == 'hibernating'">
        Your store is hibernating, please contact support for assistance.
      </p>
      <p v-else-if="store?.status == 'deactivated'">
        Your store is deactivated, please contact support for assistance.
      </p>
    </section>
  </div>
</template>
