<script setup lang="ts">
definePageMeta({ middleware: 'auth-required' })

const { api } = useApi()
const isSubmitting = ref(false)
const success = ref(false)
const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

const { form, reset } = useForm({
  current: '',
  new_password: '',
  confirm_password: '',
})

async function changePassword() {
  clearErrors()
  success.value = false

  if (form.value.new_password !== form.value.confirm_password) {
    setError({ data: { detail: 'Passwords do not match' } })
    return
  }

  isSubmitting.value = true
  try {
    await api('/auth/change-password', {
      method: 'POST',
      body: {
        current: form.value.current,
        new_password: form.value.new_password,
      },
    })
    success.value = true
    reset()
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-md px-5 py-10">
    <NuxtLink to="/account" class="text-sm font-semibold text-teal-700">← My account</NuxtLink>
    <h1 class="mt-5 text-3xl font-black">Change password</h1>

    <form
      class="mt-8 space-y-5 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      @submit.prevent="changePassword"
    >
      <div
        v-if="success"
        class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-800"
      >
        ✓ Password changed successfully. All other sessions have been logged out.
      </div>
      <div
        v-if="errorMessage"
        class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
      >
        {{ errorMessage }}
      </div>

      <label class="block text-sm font-bold">
        Current password
        <input
          v-model="form.current"
          type="password"
          required
          minlength="6"
          autocomplete="current-password"
          class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
        />
      </label>
      <label class="block text-sm font-bold">
        New password
        <input
          v-model="form.new_password"
          type="password"
          required
          minlength="6"
          autocomplete="new-password"
          class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
        />
      </label>
      <label class="block text-sm font-bold">
        Confirm new password
        <input
          v-model="form.confirm_password"
          type="password"
          required
          minlength="6"
          autocomplete="new-password"
          class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
        />
      </label>
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white disabled:opacity-60"
      >
        {{ isSubmitting ? 'Updating…' : 'Update password' }}
      </button>
    </form>
  </div>
</template>
