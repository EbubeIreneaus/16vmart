<script setup lang="ts">
import type { User, Page } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const auth = useAuthStore()
const currentPage = ref(1)
const statusFilter = ref('all')
const searchEmail = ref('')
const filterTabs = ['all', 'active', 'suspended', 'terminated', 'hibernating', 'under_review']
const statusOptions = ['active', 'suspended', 'terminated', 'hibernating', 'under_review']
const roleOptions = ['user', 'seller', 'admin', 'superadmin']

const { data: response, pending, refresh } = await useAsyncData(
  'admin-users',
  () => api<Page<User>>('/admin/users/all', {
    params: { page: currentPage.value, size: 20, s: statusFilter.value },
  }),
  {
    default: () => ({ items: [], total: 0, page: 1, size: 20, pages: 1 }),
    watch: [currentPage, statusFilter],
  }
)

// Search by email
const searchResult = ref<User | null>(null)
const searchError = ref('')
async function searchUser() {
  searchResult.value = null
  searchError.value = ''
  if (!searchEmail.value.trim()) return
  try {
    searchResult.value = await api<User>(`/admin/users/${searchEmail.value.trim()}`)
  } catch {
    searchError.value = 'User not found'
  }
}

// Change status
async function changeStatus(email: string, status: string) {
  await api('/admin/users/change-status', {
    method: 'POST',
    body: { email, status },
  })
  if (searchResult.value && searchResult.value.email.toLowerCase() === email.toLowerCase()) {
    searchResult.value.status = status as any
  }
  await refresh()
}

// Change role (superadmin only)
async function changeRole(email: string, role: string) {
  await api('/admin/users/update-role', {
    method: 'POST',
    body: { email, role },
  })
  if (searchResult.value && searchResult.value.email.toLowerCase() === email.toLowerCase()) {
    searchResult.value.role = role as any
  }
  await refresh()
}

function changePage(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Platform oversight</p>
    <h1 class="mt-2 text-4xl font-black">Users</h1>

    <!-- Search -->
    <form class="mt-6 flex gap-2" @submit.prevent="searchUser">
      <input
        v-model="searchEmail"
        type="email"
        class="min-w-0 flex-1 rounded-lg border border-slate-300 p-3 text-sm"
        placeholder="Search by email..."
      />
      <button class="rounded-lg bg-slate-950 px-5 font-bold text-white text-sm">Search</button>
    </form>

    <!-- Search result -->
    <div v-if="searchResult" class="mt-4 rounded-2xl bg-teal-50 p-5 ring-1 ring-teal-200">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p class="font-black">{{ searchResult.fullname }}</p>
          <p class="text-sm text-slate-500">{{ searchResult.email }}</p>
        </div>
        <div class="flex flex-wrap gap-2 items-center">
          <span class="rounded-full bg-white px-3 py-1 text-xs font-bold capitalize">{{ searchResult.role }}</span>
          <select
            class="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-bold capitalize"
            :value="searchResult.status"
            @change="changeStatus(searchResult.email, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
          </select>
          <select
            v-if="auth.isSuperAdmin"
            class="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs font-bold capitalize"
            :value="searchResult.role"
            @change="changeRole(searchResult.email, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
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

    <!-- User list -->
    <div v-if="pending" class="mt-5 space-y-3">
      <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-lg bg-slate-200" />
    </div>

    <div v-else class="mt-5 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div
        v-for="user in response.items"
        :key="user.id"
        class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 py-4 last:border-0"
      >
        <div>
          <p class="font-black">{{ user.fullname }}</p>
          <p class="text-sm text-slate-500">{{ user.email }}</p>
        </div>
        <div class="flex flex-wrap gap-2 items-center">
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold capitalize">{{ user.role }}</span>
          <select
            class="rounded-lg border border-slate-300 px-2 py-1 text-xs font-bold capitalize"
            :value="user.status"
            @change="changeStatus(user.email, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
          </select>
          <select
            v-if="auth.isSuperAdmin"
            class="rounded-lg border border-slate-300 px-2 py-1 text-xs font-bold capitalize"
            :value="user.role"
            @change="changeRole(user.email, ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>
      <div v-if="response.items.length < 1" class="py-8 text-center text-slate-500">
        No users found for this status filter.
      </div>
    </div>

    <AppPagination :page="response" @change="changePage" />
  </div>
</template>
