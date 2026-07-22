<script setup lang="ts">
import FormErrorLabel from "~/components/FormErrorLabel.vue";
import type { Store } from "~/types/api";
import { INDUSTRY_CHOICES } from "~/lib/industries";

const { form } = useForm({
  name: "",
  industry: "",
  email: "",
  phone: "",
  state: "",
  city: "",
  address: "",
});
const {
  fields: errorFields,
  message: errorMessage,
  setError,
} = useGetAPIFormError();
const isLoading = ref(false);
const config = useRuntimeConfig();
const access_token = useCookie("access_token").value;

async function createStore() {
  isLoading.value = true;
  setError("");
  try {
    const res = await $fetch(`${config.public.apiUrl}/store/entity`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
      body: form.value,
    });
    await navigateTo("/vendor");
  } catch (error: any) {
    setError(error);
  } finally {
    isLoading.value = false;
  }
}
</script>
<template>
  <div class="mx-auto max-w-3xl px-5 py-10">
    <NuxtLink to="/vendor" class="text-sm font-bold text-teal-700"
      >← My stores</NuxtLink
    >
    <p class="mt-7 text-sm font-bold uppercase tracking-widest text-teal-700">
      Seller onboarding
    </p>
    <h1 class="mt-2 text-4xl font-black">Create a store</h1>
    <p class="mt-2 text-slate-600">
      This is a mock of the API’s StoreSchemaIn payload. Your store will be
      submitted for review after live integration.
    </p>
    <form
      class="mt-8 space-y-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      @submit.prevent="createStore"
    >
      <p
        v-if="errorMessage"
        class="rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-700"
      >
        {{ errorMessage }}
      </p>
      <div class="grid gap-5 md:grid-cols-2">
        <label class="text-sm font-bold"
          >Business name<input
            v-model.trim="form.name"
            required
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            placeholder="e.g. Atlas Lifestyle"
          />
          <FormErrorLabel
            :message="errorFields.name"
            v-if="errorFields.name"
          /> </label
        ><label class="text-sm font-bold"
          >Industry<select
            v-model.trim="form.industry"
            required
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            placeholder="e.g. Fashion & accessories"
          >
            <option value="">Select industry</option>
            <option
              v-for="industry in INDUSTRY_CHOICES"
              :key="industry"
              :value="industry"
            >
              {{ industry }}
            </option>
          </select>
          <FormErrorLabel
            :message="errorFields.industry"
            v-if="errorFields.industry"
          />
        </label>
      </div>
      <div class="grid gap-5 md:grid-cols-2">
        <label class="text-sm font-bold"
          >Business email<input
            v-model.trim="form.email"
            required
            type="email"
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
          />
          <FormErrorLabel
            :message="errorFields.email"
            v-if="errorFields.email"
          />
        </label>

        <label class="text-sm font-bold"
          >Phone number<input
            v-model.trim="form.phone"
            required
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            placeholder="+234..."
          />
          <FormErrorLabel
            :message="errorFields.phone"
            v-if="errorFields.phone"
          />
        </label>
      </div>
      <div class="grid gap-5 md:grid-cols-2">
        <label class="text-sm font-bold"
          >State<input
            v-model.trim="form.state"
            required
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            placeholder="Lagos"
          />
          <FormErrorLabel
            :message="errorFields.state"
            v-if="errorFields.state"
          />
        </label>

        <label class="text-sm font-bold"
          >City<input
            v-model.trim="form.city"
            required
            class="mt-2 w-full rounded-lg border border-slate-300 p-3"
            placeholder="Lekki"
          />
          <FormErrorLabel :message="errorFields.city" v-if="errorFields.city" />
        </label>
      </div>
      <label class="block text-sm font-bold"
        >Business address<input
          v-model.trim="form.address"
          required
          class="mt-2 w-full rounded-lg border border-slate-300 p-3"
        />
        <FormErrorLabel
          :message="errorFields.address"
          v-if="errorFields.address"
        /> </label
      ><button class="w-full rounded-xl bg-teal-700 py-3 font-bold text-white">
        Create store
      </button>
    </form>
  </div>
</template>
