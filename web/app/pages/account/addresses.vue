<script setup lang="ts">
import type { Address, AddressIn } from '~/types/api'

definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()
const showForm = ref(false)
const isSubmitting = ref(false)
const {
  fields: errorFields,
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

const { data: addresses, refresh } = await useAsyncData('my-addresses', () =>
  api<Address[]>('/user/address'),
  { default: () => [] }
)

const { form: newAddress, reset } = useForm<AddressIn>({
  state: '',
  city: '',
  landmark: '',
  line_1: '',
  line_2: '',
  zip_code: 0,
})

async function createAddress() {
  clearErrors()
  isSubmitting.value = true
  try {
    await api('/user/create-address', {
      method: 'POST',
      body: newAddress.value,
    })
    reset()
    showForm.value = false
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}

async function deleteAddress(addressId: string) {
  await api(`/user/address/${addressId}`, { method: 'DELETE' })
  await refresh()
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-5 py-10">
    <NuxtLink to="/account" class="text-sm font-semibold text-teal-700">← My account</NuxtLink>
    <div class="mt-5 flex items-end justify-between">
      <h1 class="text-4xl font-black">My addresses</h1>
      <button
        class="rounded-xl bg-teal-700 px-5 py-2.5 font-bold text-white"
        @click="showForm = !showForm"
      >
        {{ showForm ? 'Cancel' : '+ Add address' }}
      </button>
    </div>

    <!-- New address form -->
    <form
      v-if="showForm"
      class="mt-6 space-y-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      @submit.prevent="createAddress"
    >
      <p v-if="errorMessage" class="rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-700">
        {{ errorMessage }}
      </p>
      <div class="grid gap-4 md:grid-cols-2">
        <label class="text-sm font-bold">
          State
          <input v-model="newAddress.state" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
        <label class="text-sm font-bold">
          City
          <input v-model="newAddress.city" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
      </div>
      <label class="block text-sm font-bold">
        Address line 1
        <input v-model="newAddress.line_1" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
      </label>
      <label class="block text-sm font-bold">
        Address line 2 (optional)
        <input v-model="newAddress.line_2" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
      </label>
      <div class="grid gap-4 md:grid-cols-2">
        <label class="text-sm font-bold">
          ZIP code
          <input v-model.number="newAddress.zip_code" type="number" required class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
        <label class="text-sm font-bold">
          Landmark (optional)
          <input v-model="newAddress.landmark" class="mt-2 w-full rounded-lg border border-slate-300 p-3" />
        </label>
      </div>
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white disabled:opacity-60"
      >
        {{ isSubmitting ? 'Saving…' : 'Save address' }}
      </button>
    </form>

    <!-- Address list -->
    <div v-if="addresses.length" class="mt-6 space-y-3">
      <div
        v-for="addr in addresses"
        :key="addr.address_id"
        class="flex items-start justify-between rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200"
      >
        <div>
          <p class="font-bold">{{ addr.line_1 }}</p>
          <p v-if="addr.line_2" class="text-sm text-slate-500">{{ addr.line_2 }}</p>
          <p class="text-sm text-slate-500">{{ addr.city }}, {{ addr.state }} · {{ addr.zip_code }}</p>
          <p v-if="addr.landmark" class="text-sm text-slate-400">Landmark: {{ addr.landmark }}</p>
        </div>
        <button
          class="text-sm font-bold text-rose-600"
          @click="deleteAddress(addr.address_id)"
        >
          Delete
        </button>
      </div>
    </div>
    <div v-else-if="!showForm" class="mt-6 rounded-2xl border border-dashed border-slate-300 p-8 text-center">
      <p class="text-slate-500">No saved addresses yet.</p>
    </div>
  </div>
</template>
