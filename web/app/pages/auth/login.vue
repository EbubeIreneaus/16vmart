<template>
  <div class="mx-auto max-w-md px-5 py-16">
    <AppLogo />
    <section
      class="mt-8 rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200"
    >
      <p class="text-sm font-bold uppercase tracking-widest text-teal-700">
        Welcome back
      </p>
      <h1 class="mt-2 text-3xl font-black">Sign in to 16Vmart</h1>
      <form class="mt-6 space-y-4" @submit.prevent="login">
        <div
          v-if="formError"
          class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
          role="alert"
        >
          {{ formError }}
        </div>
        <label class="block text-sm font-bold"
          >Email<input
            v-model.trim="form.email"
            type="email"
            autocomplete="email"
            :aria-invalid="Boolean(fieldErrors.email)"
            class="mt-2 w-full rounded-lg border p-3 outline-none focus:ring-2 focus:ring-teal-500"
            :class="fieldErrors.email ? 'border-rose-400' : 'border-slate-300'"
            placeholder="you@example.com"
          />
          <span
            v-if="fieldErrors.email"
            class="mt-1 block text-xs font-medium text-rose-600"
            >{{ fieldErrors.email }}</span
          >
        </label>
        <label class="block text-sm font-bold"
          >Password<input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            :aria-invalid="Boolean(fieldErrors.password)"
            class="mt-2 w-full rounded-lg border p-3 outline-none focus:ring-2 focus:ring-teal-500"
            :class="
              fieldErrors.password ? 'border-rose-400' : 'border-slate-300'
            "
        /></label>
        <span
          v-if="fieldErrors.password"
          class="-mt-3 block text-xs font-medium text-rose-600"
          >{{ fieldErrors.password }}</span
        >
        <button
          :disabled="isSubmitting"
          class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ isSubmitting ? "Signing in…" : "Sign in" }}
        </button>
      </form>
      <p class="mt-5 text-sm text-slate-600">
        New here?
        <NuxtLink to="/register" class="font-bold text-teal-700">
          Create an account</NuxtLink
        >
      </p>
    </section>
  </div>
</template>

<script lang="ts" setup>
const { form, reset } = useForm({
  email: "",
  password: "",
});

const redirect = useRoute().query.redirect as string | null

const config = useRuntimeConfig();
const isSubmitting = ref(false);
const {
  fields: fieldErrors,
  message: formError,
  setError,
  clearErrors,
} = useGetAPIFormError();

async function login() {
  clearErrors();
  isSubmitting.value = true;

  try {
    await $fetch(`${config.public.apiUrl}/auth/signin`, {
      method: "POST",
      body: form.value,
      credentials: "include",
    });
    await navigateTo(redirect || "/");
  } catch (error) {
    setError(error);
  } finally {
    reset();
    isSubmitting.value = false;
  }
}
</script>
