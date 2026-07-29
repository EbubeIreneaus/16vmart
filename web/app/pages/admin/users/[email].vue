<script setup lang="ts">
import type { UserWithDetails } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const { api } = useApi()
const auth = useAuthStore()

const email = computed(() => String(route.params.email))

const { data: user, pending, error, refresh } = await useAsyncData(
  `admin-user-${email.value}`,
  () => api<UserWithDetails>(`/admin/users/${email.value}`)
)

const statusOptions = ['active', 'suspended', 'terminated', 'hibernating', 'under_review']
const roleOptions = ['user', 'seller', 'admin', 'superadmin']

async function changeStatus(status: string) {
  if (!user.value) return
  await api('/admin/users/change-status', {
    method: 'POST',
    body: { email: user.value.email, status },
  })
  user.value.status = status as any
  await refresh()
}

async function changeRole(role: string) {
  if (!user.value) return
  await api('/admin/users/update-role', {
    method: 'POST',
    body: { email: user.value.email, role },
  })
  user.value.role = role as any
  await refresh()
}
</script>

<template>
  <div class="mx-auto max-w-5xl">
    <div class="flex items-center gap-3">
      <NuxtLink
        to="/admin/users"
        class="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-teal-700 transition"
      >
        ← Back to Users
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="mt-6 space-y-4">
      <div class="h-10 w-48 animate-pulse rounded-lg bg-slate-200" />
      <div class="h-48 animate-pulse rounded-2xl bg-slate-200" />
    </div>

    <!-- Error -->
    <div v-else-if="error || !user" class="mt-6 rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
      <h2 class="text-xl font-black text-slate-900">User Not Found</h2>
      <p class="mt-1 text-sm text-slate-500">The requested user account could not be loaded.</p>
      <NuxtLink to="/admin/users" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2 text-xs font-bold text-white">
        Return to Users
      </NuxtLink>
    </div>

    <!-- Details -->
    <div v-else class="mt-6 space-y-6">
      <!-- User Header Card -->
      <div class="rounded-3xl bg-slate-950 p-6 text-white shadow-xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-black uppercase tracking-widest text-teal-400">User Account</p>
          <h1 class="mt-1 text-3xl font-black">{{ user.fullname }}</h1>
          <p class="mt-1 text-xs text-slate-400">{{ user.email }}</p>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <span
            class="rounded-full px-3 py-1 text-xs font-bold capitalize"
            :class="user.email_verified ? 'bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/50' : 'bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/50'"
          >
            {{ user.email_verified ? 'Email Verified' : 'Unverified' }}
          </span>

          <div class="flex items-center gap-2">
            <label class="text-xs font-bold text-slate-400">Status:</label>
            <select
              class="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-bold capitalize text-white outline-none focus:border-teal-500"
              :value="user.status"
              @change="changeStatus(($event.target as HTMLSelectElement).value)"
            >
              <option v-for="s in statusOptions" :key="s" :value="s">{{ s.replace('_', ' ') }}</option>
            </select>
          </div>

          <div v-if="auth.isSuperAdmin" class="flex items-center gap-2">
            <label class="text-xs font-bold text-slate-400">Role:</label>
            <select
              class="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-bold capitalize text-white outline-none focus:border-teal-500"
              :value="user.role"
              @change="changeRole(($event.target as HTMLSelectElement).value)"
            >
              <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="grid gap-6 md:grid-cols-2">
        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Account Details</p>
          <div class="mt-3 space-y-2 text-sm text-slate-700">
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">User ID</span>
              <span class="font-bold text-slate-900">#{{ user.id }}</span>
            </div>
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Full Name</span>
              <span class="font-bold text-slate-900">{{ user.fullname }}</span>
            </div>
            <div class="flex justify-between border-b border-slate-100 pb-2">
              <span class="text-slate-500">Email Address</span>
              <span class="font-bold text-slate-900">{{ user.email }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Platform Role</span>
              <span class="font-bold capitalize text-slate-900">{{ user.role }}</span>
            </div>
          </div>
        </div>

        <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Associated Stores</p>
          <p class="mt-1 text-2xl font-black text-slate-900">{{ user.stores?.length || 0 }} Stores Owned</p>
          <div v-if="user.stores && user.stores.length" class="mt-3 space-y-2">
            <NuxtLink
              v-for="st in user.stores"
              :key="st.slug"
              :to="`/admin/stores/${st.slug}`"
              class="flex items-center justify-between rounded-xl bg-slate-50 p-3 hover:bg-slate-100 transition ring-1 ring-slate-200/80"
            >
              <div>
                <p class="font-bold text-slate-900 text-sm">{{ st.name }}</p>
                <p class="text-xs text-slate-500">{{ st.industry }} · {{ st.city }}</p>
              </div>
              <span class="rounded-full bg-white px-2.5 py-0.5 text-xs font-bold capitalize text-slate-700">
                {{ st.status }}
              </span>
            </NuxtLink>
          </div>
          <p v-else class="mt-2 text-xs text-slate-400">This user does not own any registered stores.</p>
        </div>
      </div>

      <!-- Login Sessions -->
      <div v-if="user.sessions && user.sessions.length" class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 class="text-lg font-black text-slate-900">Active Login Sessions</h2>
        <p class="text-xs text-slate-500 mt-0.5">Recent active sessions and security tokens associated with this user.</p>

        <div class="mt-4 divide-y divide-slate-100">
          <div
            v-for="sess in user.sessions"
            :key="sess.id"
            class="flex flex-wrap items-center justify-between gap-3 py-3"
          >
            <div>
              <p class="font-bold text-slate-900 text-sm">{{ sess.device || 'Unknown Device' }}</p>
              <p class="text-xs text-slate-500">
                IP: {{ sess.ip_address || 'N/A' }} · Location: {{ sess.location || 'Unknown' }}
              </p>
            </div>
            <div class="text-right text-xs text-slate-500">
              <p>Logged in: {{ new Date(sess.created_at).toLocaleString() }}</p>
              <p>Expires: {{ new Date(sess.expired_at).toLocaleString() }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
