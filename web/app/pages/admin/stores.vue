<script setup lang="ts">
import type { Store, StoreWithUser, Page } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const currentPage = ref(1)

const { data: response, pending, refresh } = await useAsyncData(
  'admin-stores',
  () => api<Page<Store>>('/admin/stores/all', {
    params: { page: currentPage.value, size: 20 },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage],
  }
)

// Status update
const statusOptions = ['active', 'suspended', 'terminated', 'hibernating', 'under_review', 'deactivated']

async function updateStatus(slug: string, status: string) {
  await api('/admin/stores/update-status', {
    method: 'POST',
    body: { slug, status },
  })
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
      // Get full detail of first result
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
      <div class="flex items-start justify-between">
        <div>
          <p class="font-black">{{ searchResult.name }}</p>
          <p class="text-sm text-slate-500">{{ searchResult.industry }} · {{ searchResult.city }}, {{ searchResult.state }}</p>
          <p class="mt-1 text-xs text-slate-400">Owner: {{ searchResult.user?.fullname }} ({{ searchResult.user?.email }})</p>
        </div>
        <span class="rounded-full px-3 py-1 text-xs font-bold capitalize bg-white">{{ searchResult.status.replace('_', ' ') }}</span>
      </div>
      <button class="mt-2 text-sm font-bold text-teal-700" @click="searchResult = null">Close</button>
    </div>
    <p v-if="searchError" class="mt-4 text-sm text-rose-600">{{ searchError }}</p>

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
          <p class="font-black">{{ store.name }}</p>
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
