<template>
  <div class="mx-auto max-w-md px-5 py-16">
    <AppLogo />
    <section
      class="mt-8 rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200"
    >
      <p class="text-sm font-bold uppercase tracking-widest text-teal-700">
        Start shopping
      </p>
      <h1 class="mt-2 text-3xl font-black">Create your account</h1>
      <form class="mt-6 space-y-4" @submit.prevent="Register">
        <div
          v-if="errorMessage"
          class="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-800"
          role="alert"
        >
          {{ errorMessage }}
        </div>

        <label class="block text-sm font-bold"
          >Full name<input
            v-model="form.fullname"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            minlength="3"
        /></label>
        <span
          v-if="errorFields.fullname"
          class="mt-1 block text-xs font-medium text-rose-600"
          >{{ errorFields.fullname }}</span
        >
        <label class="block text-sm font-bold"
          >Email<input
            v-model="form.email"
            type="email"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
        /></label>
        <span
          v-if="errorFields.email"
          class="mt-1 block text-xs font-medium text-rose-600"
          >{{ errorFields.email }}</span
        >
        <label class="block text-sm font-bold"
          >Password<input
            v-model="form.password"
            type="password"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            minlength="6"
          />
          <span
            v-if="errorFields.password"
            class="mt-1 block text-xs font-medium text-rose-600"
            >{{ errorFields.password }}</span
          > </label
        ><u-button
          class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white "
          :ui="{
            base: 'justify-center'
          }"
          type="submit"
          label="Create account"
          :loading="isLoading"
          :disabled="isLoading"
        >
          
        </u-button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
const { form, reset } = useForm({
  fullname: "",
  email: "",
  password: "",
});
const isLoading = ref(false);
const config = useRuntimeConfig();
const {
  fields: errorFields,
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError();

async function Register() {
  clearErrors();
  isLoading.value = true;
  try {
    const res = await $fetch(`${config.public.apiUrl}/auth/signup`, {
      method: "POST",
      body: form.value,
    });
    await navigateTo("/");
  } catch (error) {
    setError(error);
  } finally {
    isLoading.value = false;
  }
}
</script>
