<script setup lang="ts">
import type { Store } from '~/types/api'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const storeSlug = String(route.params.store)
const { api } = useApi()
const isSubmitting = ref(false)
const success = ref(false)
const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

const { data: store, refresh } = await useAsyncData(
  `vendor-settings-${storeSlug}`,
  () => api<Store>(`/store/entity/${storeSlug}`),
)

const { form } = useForm({
  name: store.value?.name || '',
  phone: store.value?.phone || '',
  email: store.value?.email || '',
  address: store.value?.address || '',
  industry: store.value?.industry || '',
  state: store.value?.state || '',
  city: store.value?.city || '',
})

// Sync form when data loads
watch(store, (s) => {
  if (s) {
    form.value = {
      name: s.name,
      phone: s.phone,
      email: s.email,
      address: s.address,
      industry: s.industry,
      state: s.state,
      city: s.city,
    }
  }
}, { immediate: true })

async function saveProfile() {
  clearErrors()
  isSubmitting.value = true
  success.value = false
  try {
    await api(`/store/entity/${storeSlug}`, {
      method: 'PATCH',
      body: form.value,
    })
    success.value = true
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}

// Logo upload
const uploadingLogo = ref(false)
async function uploadLogo(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files?.[0]) return

  uploadingLogo.value = true
  try {
    const formData = new FormData()
    formData.append('file', target.files[0])
    await api(`/store/entity/${storeSlug}/logo`, {
      method: 'PATCH',
      body: formData,
    })
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    uploadingLogo.value = false
  }
}
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Store settings</p>
    <h1 class="mt-2 text-4xl font-black">Store profile</h1>

    <!-- Logo -->
    <div class="mt-8 flex items-center gap-5">
      <div class="grid size-20 place-items-center rounded-2xl bg-teal-100 text-3xl font-black text-teal-800 overflow-hidden">
        <img v-if="store?.logo" :src="store.logo" alt="Store logo" class="size-full object-cover" />
        <span v-else>{{ store?.name?.charAt(0) || '?' }}</span>
      </div>
      <div>
        <p class="text-sm font-bold">Store logo</p>
        <label class="mt-1 inline-block cursor-pointer rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-bold">
          {{ uploadingLogo ? 'Uploading…' : 'Upload logo' }}
          <input type="file" accept="image/*" class="hidden" @change="uploadLogo" />
        </label>
      </div>
    </div>

    <form class="mt-8 max-w-2xl space-y-5 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200" @submit.prevent="saveProfile">
      <div
        v-if="success"
        class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-800"
      >
        ✓ Store profile updated successfully.
      </div>
      <p v-if="errorMessage" class="rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-700">
        {{ errorMessage }}
      </p>

      <label class="block text-sm font-bold">
        Store name
        <input v-model="form.name" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
      </label>
      <div class="grid gap-5 md:grid-cols-2">
        <label class="text-sm font-bold">
          Phone
          <input v-model="form.phone" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
        <label class="text-sm font-bold">
          Email
          <input v-model="form.email" type="email" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
      </div>
      <div class="grid gap-5 md:grid-cols-2">
        <label class="text-sm font-bold">
          State
          <input v-model="form.state" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
        <label class="text-sm font-bold">
          City
          <input v-model="form.city" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
      </div>
      <label class="block text-sm font-bold">
        Address
        <input v-model="form.address" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
      </label>
      <button
        type="submit"
        :disabled="isSubmitting"
        class="rounded-xl bg-teal-700 px-5 py-3 font-bold text-white disabled:opacity-60"
      >
        {{ isSubmitting ? 'Saving…' : 'Save profile' }}
      </button>
    </form>
  </div>
</template>
