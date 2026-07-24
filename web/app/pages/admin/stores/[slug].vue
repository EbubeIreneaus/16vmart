<script setup lang="ts">
import type { StoreWithUser } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const { api } = useApi()

const slug = computed(() => String(route.params.slug))

const { data: store, pending, error, refresh } = await useAsyncData(
  `admin-store-${slug.value}`,
  () => api<StoreWithUser>(`/admin/stores/${slug.value}`)
)

const statusOptions = ['active', 'suspended', 'terminated', 'hibernating', 'under_review', 'deactivated']

async function updateStatus(status: string) {
  if (!store.value) return
  await api('/admin/stores/update-status', {
    method: 'POST',
    body: { slug: store.value.slug, status },
  })
  store.value.status = status as any
  await refresh()
}
</script>

<template>
  <div class="mx-auto max-w-5xl">
    <div class="flex items-center gap-3">
      <NuxtLink
        to="/admin/stores"
        class="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-teal-700 transition"
      >
        ← Back to Stores
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="mt-6 space-y-4">
      <div class="h-10 w-48 animate-pulse rounded-lg bg-slate-200" />
      <div class="h-48 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Error -->
    <div v-else-if="error || !store" class="mt-6 rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black text-slate-900">Store Not Found</h2>
      <p class="mt-1 text-sm text-slate-500">The requested store profile could not be loaded.</p>
      <NuxtLink to="/admin/stores" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2 text-xs font-bold text-white">
        Return to Stores
      </NuxtLink>
    </div>

    <!-- Details -->
    <div v-else class="mt-6 space-y-6">
      <!-- Store Header Card -->
      <div class="rounded-3xl bg-slate-950 p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <img
            v-if="store.logo"
            :src="store.logo"
            :alt="store.name"
            class="h-16 w-16 rounded-2xl object-cover ring-2 ring-teal-400/50"
          />
          <div v-else class="h-16 w-16 rounded-2xl bg-slate-800 flex items-center justify-center font-black text-xl text-teal-400">
            {{ store.name?.charAt(0).toUpperCase() }}
          </div>
          <div>
            <p class="text-xs font-black uppercase tracking-widest text-teal-400">Store Moderation</p>
            <h1 class="mt-1 text-3xl font-black">{{ store.name }}</h1>
            <p class="mt-1 text-xs text-slate-400">{{ store.industry }} · {{ store.city }}, {{ store.state }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <label class="text-xs font-bold text-slate-400">Status:</label>
          <select
            class="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-bold capitalize text-white outline-none focus:border-teal-500"
            :value="store.status"
            @change="updateStatus(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
          </select>
        </div>
      </div>

      <!-- Details Cards Grid -->
      <div class="grid gap-6 md:grid-cols-2">
        <!-- Store Information -->
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Contact & Location Info</p>
          <div class="mt-3 space-y-2 text-sm text-slate-700">
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Store Slug</span>
              <span class="font-bold text-slate-900">{{ store.slug }}</span>
            </div>
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Phone Number</span>
              <span class="font-bold text-slate-900">{{ store.phone }}</span>
            </div>
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Business Email</span>
              <span class="font-bold text-slate-900">{{ store.email }}</span>
            </div>
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Industry</span>
              <span class="font-bold text-slate-900 capitalize">{{ store.industry }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Address</span>
              <span class="font-bold text-slate-900 text-right">{{ store.address }}, {{ store.city }}, {{ store.state }}</span>
            </div>
          </div>
        </div>

        <!-- Owner Information -->
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Store Owner Profile</p>
          <div v-if="store.user" class="mt-3">
            <h2 class="text-lg font-black text-slate-900">{{ store.user.fullname }}</h2>
            <p class="text-sm text-slate-600 mt-0.5">{{ store.user.email }}</p>
            <div class="mt-3 flex items-center gap-2">
              <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold capitalize text-slate-700">
                Role: {{ store.user.role }}
              </span>
              <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold capitalize text-slate-700">
                Status: {{ store.user.status }}
              </span>
            </div>
            <div class="mt-5">
              <NuxtLink
                :to="`/admin/users/${store.user.email}`"
                class="inline-block rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition"
              >
                View Owner Profile →
              </NuxtLink>
            </div>
          </div>
          <p v-else class="mt-2 text-xs text-slate-400">No owner information linked to this store.</p>
        </div>
      </div>
    </div>
  </div>
</template>
