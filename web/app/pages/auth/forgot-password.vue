<template>
  <div class="mx-auto max-w-md px-5 py-16">
    <AppLogo />
    <section class="mt-8 rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200">
      <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Account recovery</p>
      <h1 class="mt-2 text-3xl font-black">Forgot your password?</h1>
      <p class="mt-2 text-sm text-slate-600">
        Enter your email address and we'll send you a link to reset your password.
      </p>

      <div
        v-if="success"
        class="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-800"
      >
        ✓ Reset link sent! Check your email inbox (and spam folder) for the password reset link.
      </div>

      <form v-else class="mt-6 space-y-4" @submit.prevent="sendResetLink">
        <div
          v-if="formError"
          class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
          role="alert"
        >
          {{ formError }}
        </div>
        <label class="block text-sm font-bold">
          Email
          <input
            v-model.trim="email"
            type="email"
            required
            autocomplete="email"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3 outline-none focus:ring-2 focus:ring-teal-500"
            placeholder="you@example.com"
          />
        </label>
        <button
          :disabled="isSubmitting"
          class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ isSubmitting ? 'Sending…' : 'Send reset link' }}
        </button>
      </form>

      <p class="mt-5 text-sm text-slate-600">
        Remember your password?
        <NuxtLink to="/auth/login" class="font-bold text-teal-700">Sign in</NuxtLink>
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const email = ref('')
const isSubmitting = ref(false)
const success = ref(false)
const {
  message: formError,
  setError,
  clearErrors,
} = useGetAPIFormError()

async function sendResetLink() {
  clearErrors()
  isSubmitting.value = true
  try {
    await $fetch(`${config.public.apiUrl}/auth/send-reset-link`, {
      method: 'POST',
      body: { email: email.value },
    })
    success.value = true
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
