<template>
  <div class="mx-auto max-w-md px-5 py-16">
    <AppLogo />
    <section class="mt-8 rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200">
      <!-- Invalid/expired token -->
      <template v-if="tokenError">
        <h1 class="text-3xl font-black text-rose-700">Invalid reset link</h1>
        <p class="mt-3 text-slate-600">{{ tokenError }}</p>
        <NuxtLink
          to="/auth/forgot-password"
          class="mt-6 inline-block rounded-xl bg-teal-700 px-5 py-3 font-bold text-white"
        >
          Request a new link
        </NuxtLink>
      </template>

      <!-- Success -->
      <template v-else-if="success">
        <h1 class="text-3xl font-black text-emerald-700">Password reset!</h1>
        <p class="mt-3 text-slate-600">
          Your password has been updated successfully. You can now sign in with your new password.
        </p>
        <NuxtLink
          to="/auth/login"
          class="mt-6 inline-block rounded-xl bg-teal-700 px-5 py-3 font-bold text-white"
        >
          Sign in
        </NuxtLink>
      </template>

      <!-- Reset form -->
      <template v-else>
        <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Account recovery</p>
        <h1 class="mt-2 text-3xl font-black">Set a new password</h1>
        <form class="mt-6 space-y-4" @submit.prevent="resetPassword">
          <div
            v-if="formError"
            class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
            role="alert"
          >
            {{ formError }}
          </div>
          <label class="block text-sm font-bold">
            New password
            <input
              v-model="newPassword"
              type="password"
              required
              minlength="6"
              autocomplete="new-password"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
            />
          </label>
          <label class="block text-sm font-bold">
            Confirm password
            <input
              v-model="confirmPassword"
              type="password"
              required
              minlength="6"
              autocomplete="new-password"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
            />
          </label>
          <button
            :disabled="isSubmitting"
            class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ isSubmitting ? 'Resetting…' : 'Reset password' }}
          </button>
        </form>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()

// The token comes as a catch-all param — join it back with /
const rawToken = computed(() => {
  const params = route.params.token
  return Array.isArray(params) ? params.join('/') : params
})

const tokenError = ref('')
const success = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const {
  message: formError,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Validate the reset link on mount
onMounted(async () => {
  try {
    await $fetch(`${config.public.apiUrl}/auth/validate-reset-link`, {
      params: { q: rawToken.value },
    })
  } catch (error: any) {
    const detail = error?.response?._data?.detail || error?.data?.detail
    tokenError.value = typeof detail === 'string'
      ? detail
      : 'This reset link is invalid or has expired. Please request a new one.'
  }
})

async function resetPassword() {
  clearErrors()

  if (newPassword.value !== confirmPassword.value) {
    setError({ data: { detail: 'Passwords do not match' } })
    return
  }

  isSubmitting.value = true
  try {
    await $fetch(`${config.public.apiUrl}/auth/reset-password`, {
      method: 'POST',
      body: {
        new_password: newPassword.value,
        token: rawToken.value,
      },
    })
    success.value = true
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
