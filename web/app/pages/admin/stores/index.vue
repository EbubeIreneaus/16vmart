<script setup lang="ts">
import type { Store, StoreWithUser, Page } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const currentPage = ref(1)
const statusFilter = ref('all')
const filterTabs = ['all', 'active', 'suspended', 'terminated', 'hibernating', 'under_review', 'deactivated']
const statusOptions = ['active', 'suspended', 'terminated', 'hibernating', 'under_review', 'deactivated']

const { data: response, pending, refresh } = await useAsyncData(
  'admin-stores',
  () => api<Page<Store>>('/admin/stores/all', {
    params: { page: currentPage.value, size: 20, s: statusFilter.value },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage, statusFilter],
  }
)

// Status update
async function updateStatus(slug: string, status: string) {
  await api('/admin/stores/update-status', {
    method: 'POST',
    body: { slug, status },
  })
  if (searchResult.value && searchResult.value.slug.toLowerCase() === slug.toLowerCase()) {
    searchResult.value.status = status as any
  }
  await refresh()
}

// Search
const searchQuery = ref('')
const searchResult = ref<StoreWithUser | null>(null)
const searchError = ref('')
async function searchStore() {
  searchResult.value = null
  searchError.value = ''
  if (!searchQuery.value.trim()) return
  try {
    const results = await api<Page<Store>>('/admin/stores/search', {
      params: { s: searchQuery.value.trim() },
    })
    if (results.items.length > 0) {
      searchResult.value = await api<StoreWithUser>(`/admin/stores/${results.items[0].slug}`)
    } else {
      searchError.value = 'No stores found'
    }
  } catch {
    searchError.value = 'Store not found'
  }
}

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Moderation</p>
    <h1 class="mt-2 text-4xl font-black">Stores</h1>

    <!-- Search -->
    <form class="mt-6 flex gap-2" @submit.prevent="searchStore">
      <input
        v-model="searchQuery"
        class="min-w-0 flex-1 rounded-lg border border-slate-300 p-3 text-sm"
        placeholder="Search stores by name..."
      />
      <button class="rounded-lg bg-slate-950 px-5 font-bold text-white text-sm">Search</button>
    </form>

    <!-- Search result -->
    <div v-if="searchResult" class="mt-4 rounded-2xl bg-teal-50 p-5 ring-1 ring-teal-200">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="font-black">{{ searchResult.name }}</p>
          <p class="text-sm text-slate-500">{{ searchResult.industry }} · {{ searchResult.city }}, {{ searchResult.state }}</p>
          <p class="mt-1 text-xs text-slate-400">Owner: {{ searchResult.user?.fullname }} ({{ searchResult.user?.email }})</p>
        </div>
        <select
          class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-bold capitalize"
          :value="searchResult.status"
          @change="updateStatus(searchResult.slug, ($event.target as HTMLSelectElement).value)"
        >
          <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
        </select>
      </div>
      <button class="mt-3 text-xs font-bold text-teal-700 hover:underline" @click="searchResult = null">Close Search</button>
    </div>
    <p v-if="searchError" class="mt-4 text-sm text-rose-600">{{ searchError }}</p>

    <!-- Status filter tabs -->
    <div class="mt-5 flex flex-wrap gap-2">
      <button
        v-for="status in filterTabs"
        :key="status"
        class="rounded-lg px-3 py-1.5 text-xs font-bold capitalize"
        :class="statusFilter === status ? 'bg-teal-700 text-white' : 'bg-white ring-1 ring-slate-200 hover:bg-slate-50'"
        @click="statusFilter = status; currentPage = 1"
      >
        {{ status.replace('_', ' ') }}
      </button>
    </div>

    <!-- Store list -->
    <div v-if="pending" class="mt-5 space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <div v-else class="mt-5 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div
        v-for="store in response.items"
        :key="store.slug"
        class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 py-4 last:border-0"
      >
        <div>
          <NuxtLink
            :to="`/admin/stores/${store.slug}`"
            class="font-black text-slate-900 hover:text-teal-700 hover:underline text-base"
          >
            {{ store.name }}
          </NuxtLink>
          <p class="text-sm text-slate-500">{{ store.industry }} · {{ store.city }}</p>
        </div>
        <select
          class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-bold capitalize"
          :value="store.status"
          @change="updateStatus(store.slug, ($event.target as HTMLSelectElement).value)"
        >
          <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
        </select>
      </div>
      <div v-if="response.items.length < 1" class="py-8 text-center text-slate-500">
        No stores found.
      </div>
    </div>

    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
