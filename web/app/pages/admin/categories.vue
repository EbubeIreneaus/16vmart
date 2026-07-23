<script setup lang="ts">
import type { AdminCategory, FormType } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()

const { data: categories, refresh } = await useAsyncData('admin-categories', () =>
  api<AdminCategory[]>('/admin/cat/all'),
  { default: () => [] }
)

// Create category modal
const open = ref(false)
const name = ref('')
const isSubmitting = ref(false)
const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Draft attributes
const attributeName = ref('')
const attributeType = ref<FormType>('text')
const draftAttributes = ref<{ name: string; required: boolean; form_type: FormType; options: string[] | null }[]>([])

function addAttribute() {
  if (!attributeName.value.trim()) return
  draftAttributes.value.push({
    name: attributeName.value,
    required: true,
    form_type: attributeType.value,
    options: ['select', 'multiple', 'radio'].includes(attributeType.value)
      ? ['Option one', 'Option two']
      : null,
  })
  attributeName.value = ''
}

async function createCategory() {
  clearErrors()
  if (!name.value.trim()) return

  isSubmitting.value = true
  try {
    await api('/admin/cat/create-category', {
      method: 'POST',
      body: {
        name: name.value,
        slug: name.value.toLowerCase().replaceAll(' ', '-'),
        attributes: draftAttributes.value.length > 0 ? draftAttributes.value : null,
        sub_categories: null,
      },
    })
    open.value = false
    name.value = ''
    draftAttributes.value = []
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Product taxonomy</p>
        <h1 class="mt-2 text-4xl font-black">Categories & attributes</h1>
        <p class="mt-2 text-slate-500">Parent attributes are inherited by every subcategory.</p>
      </div>
      <button class="rounded-xl bg-teal-700 px-5 py-3 font-bold text-white" @click="open = true">
        + New category
      </button>
    </div>

    <div class="mt-8 grid gap-5 lg:grid-cols-2">
      <article
        v-for="category in categories"
        :key="category.id"
        class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200"
      >
        <div class="flex justify-between">
          <h2 class="text-xl font-black">{{ category.name }}</h2>
          <span class="text-sm font-bold text-slate-400">{{ category.slug }}</span>
        </div>

        <section class="mt-5 rounded-xl bg-teal-50 p-4">
          <p class="text-xs font-bold uppercase tracking-wider text-teal-700">Shared attributes · inherited</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="attr in category.attributes"
              :key="attr.id"
              class="rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700"
            >
              {{ attr.name }} · {{ attr.form_type }}
            </span>
            <span v-if="!category.attributes?.length" class="text-sm text-slate-500">None defined</span>
          </div>
        </section>

        <section class="mt-4">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Subcategories</p>
          <div class="mt-3 space-y-3">
            <div
              v-for="sub in category.sub_categories"
              :key="sub.id"
              class="rounded-xl border border-slate-200 p-4"
            >
              <p class="font-bold">{{ sub.name }}</p>
              <p class="mt-2 text-sm text-slate-500">
                Adds:
                <span v-if="sub.attributes?.length">{{ sub.attributes.map(a => a.name).join(', ') }}</span>
                <span v-else>no unique attributes</span>
              </p>
            </div>
          </div>
        </section>
      </article>
    </div>

    <!-- Create modal -->
    <div v-if="open" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5">
      <form
        class="max-h-[90vh] w-full max-w-2xl overflow-auto rounded-2xl bg-white p-6 shadow-xl"
        @submit.prevent="createCategory"
      >
        <div class="flex justify-between">
          <h2 class="text-2xl font-black">Create top-level category</h2>
          <button type="button" class="text-2xl" @click="open = false">×</button>
        </div>

        <p v-if="errorMessage" class="mt-4 rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-700">
          {{ errorMessage }}
        </p>

        <label class="mt-5 block text-sm font-bold">
          Category name
          <input v-model="name" class="mt-2 w-full rounded-lg border border-slate-300 p-3" placeholder="e.g. Electronics" />
        </label>

        <div class="mt-6 border-t border-slate-200 pt-5">
          <h3 class="font-black">Shared attributes</h3>
          <p class="mt-1 text-sm text-slate-500">These will be inherited by each future subcategory.</p>
          <div class="mt-4 flex gap-2">
            <input
              v-model="attributeName"
              class="min-w-0 flex-1 rounded-lg border border-slate-300 p-3"
              placeholder="e.g. Brand"
            />
            <select v-model="attributeType" class="rounded-lg border border-slate-300 p-3">
              <option v-for="type in ['text','select','multiple','radio','date','boolean','number']" :key="type">
                {{ type }}
              </option>
            </select>
            <button type="button" class="rounded-lg bg-slate-950 px-4 font-bold text-white" @click="addAttribute">
              Add
            </button>
          </div>
          <div class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="(attr, i) in draftAttributes"
              :key="i"
              class="rounded-full bg-teal-100 px-3 py-1 text-sm font-bold text-teal-800"
            >
              {{ attr.name }} · {{ attr.form_type }}
            </span>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="mt-7 w-full rounded-xl bg-teal-700 px-5 py-3 font-bold text-white disabled:opacity-60"
        >
          {{ isSubmitting ? 'Creating…' : 'Create category' }}
        </button>
      </form>
    </div>
  </div>
</template>
