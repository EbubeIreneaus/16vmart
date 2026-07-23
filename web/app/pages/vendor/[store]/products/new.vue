<script setup lang="ts">
import type { AttributeKey, Category } from '~/types/api'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const storeSlug = String(route.params.store)
const { api } = useApi()
const isSubmitting = ref(false)
const {
  fields: errorFields,
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Fetch categories from store's endpoint
const { data: storeCategories } = await useAsyncData(
  `vendor-cats-${storeSlug}`,
  () => api<Category[]>(`/store/${storeSlug}/cat/all`),
  { default: () => [] }
)

const selectedCategory = ref<string | null>(null)
const selectedSubcategory = ref<string | null>(null)

const childCategories = computed(() =>
  (storeCategories.value || []).find((c: any) => c.slug === selectedCategory.value)?.sub_categories || []
)

// Fetch attributes when subcategory is selected
const fields = ref<AttributeKey[]>([])
watch(selectedSubcategory, async (catSlug) => {
  if (!catSlug) {
    fields.value = []
    return
  }
  try {
    // Find the parent to merge parent + child attributes
    const parent = (storeCategories.value || []).find((c: any) =>
      c.sub_categories?.some((s: any) => s.slug === catSlug)
    )
    const child = parent?.sub_categories?.find((s: any) => s.slug === catSlug)
    const parentAttrs = (parent as any)?.attributes || []
    const childAttrs = (child as any)?.attributes || []
    fields.value = [...parentAttrs, ...childAttrs]
  } catch {
    fields.value = []
  }
})

// Form data
const { form } = useForm({
  name: '',
  price: 0,
  description: '',
  condition: 'brand new' as 'brand new' | 'used',
  category_slug: '',
})
const values = reactive<Record<number, unknown>>({})
const imageFiles = ref<File[]>([])

function onFilesSelected(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    imageFiles.value = Array.from(target.files)
  }
}

async function saveProduct() {
  clearErrors()
  isSubmitting.value = true

  try {
    // Build attributes array
    const attributes = fields.value
      .filter(f => values[f.id] !== undefined && values[f.id] !== '')
      .map(f => ({
        name: f.name,
        type: f.form_type,
        value: values[f.id],
      }))

    // Create product
    const product = await api<{ slug: string }>(`/store/${storeSlug}/products/`, {
      method: 'POST',
      body: {
        ...form.value,
        category_slug: selectedSubcategory.value || selectedCategory.value,
        attributes,
      },
    })

    // Upload images
    if (imageFiles.value.length > 0 && product?.slug) {
      const formData = new FormData()
      imageFiles.value.forEach(file => formData.append('images', file))
      await api(`/store/${storeSlug}/products/image/${product.slug}`, {
        method: 'PATCH',
        body: formData,
      })
    }

    await navigateTo(`/vendor/${storeSlug}/products`)
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <p class="text-sm font-bold uppercase tracking-widest text-teal-700">Catalog</p>
    <h1 class="mt-2 text-4xl font-black">Add a product</h1>
    <p class="mt-2 text-slate-500">
      Fields appear from the selected subcategory and its parent category.
    </p>

    <form class="mt-8 grid gap-7 lg:grid-cols-[1fr_320px]" @submit.prevent="saveProduct">
      <section class="space-y-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <p v-if="errorMessage" class="rounded-lg bg-rose-50 p-3 text-sm font-semibold text-rose-700">
          {{ errorMessage }}
        </p>

        <!-- Category selectors -->
        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold">
            Category
            <select
              v-model="selectedCategory"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3"
              @change="selectedSubcategory = null"
            >
              <option :value="null" disabled>Select category</option>
              <option v-for="cat in storeCategories" :key="cat.slug" :value="cat.slug">
                {{ cat.name }}
              </option>
            </select>
          </label>
          <label class="text-sm font-bold">
            Subcategory
            <select
              v-model="selectedSubcategory"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3"
              :disabled="!selectedCategory"
            >
              <option :value="null" disabled>Select subcategory</option>
              <option v-for="sub in childCategories" :key="sub.slug" :value="sub.slug">
                {{ sub.name }}
              </option>
            </select>
          </label>
        </div>

        <!-- Core fields -->
        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold">
            Product name
            <input
              v-model="form.name"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3"
              placeholder="e.g. Aurora smartphone"
              required
            />
          </label>
          <label class="text-sm font-bold">
            Price ($)
            <input
              v-model.number="form.price"
              type="number"
              class="mt-2 w-full rounded-lg border border-slate-300 p-3"
              required
            />
          </label>
        </div>

        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold">
            Condition
            <select v-model="form.condition" class="mt-2 w-full rounded-lg border border-slate-300 p-3">
              <option value="brand new">Brand new</option>
              <option value="used">Used</option>
            </select>
          </label>
          <label class="text-sm font-bold">
            Product images
            <input
              type="file"
              multiple
              accept="image/*"
              class="mt-2 w-full rounded-lg border border-slate-300 p-2.5"
              @change="onFilesSelected"
            />
          </label>
        </div>

        <label class="block text-sm font-bold">
          Description
          <textarea
            v-model="form.description"
            class="mt-2 min-h-28 w-full rounded-lg border border-slate-300 p-3"
            required
          />
        </label>

        <!-- Dynamic attributes -->
        <div v-if="fields.length" class="border-t border-slate-200 pt-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-black">Product attributes</h2>
            <span class="text-xs font-bold text-teal-700">{{ fields.length }} required by category</span>
          </div>
          <div class="mt-5 grid gap-5 md:grid-cols-2">
            <label v-for="field in fields" :key="field.id" class="text-sm font-bold">
              {{ field.name }} <span v-if="field.required" class="text-rose-600">*</span>
              <template v-if="field.form_type === 'select' || field.form_type === 'radio'">
                <select v-model="values[field.id]" class="mt-2 w-full rounded-lg border border-slate-300 p-3">
                  <option disabled value="">Select {{ field.name }}</option>
                  <option v-for="option in field.options" :key="option">{{ option }}</option>
                </select>
              </template>
              <template v-else-if="field.form_type === 'multiple'">
                <select v-model="values[field.id]" multiple class="mt-2 min-h-28 w-full rounded-lg border border-slate-300 p-3">
                  <option v-for="option in field.options" :key="option">{{ option }}</option>
                </select>
              </template>
              <input
                v-else-if="field.form_type === 'boolean'"
                v-model="values[field.id]"
                type="checkbox"
                class="mt-3 size-5"
              />
              <input
                v-else
                :type="field.form_type === 'number' ? 'number' : field.form_type === 'date' ? 'date' : 'text'"
                v-model="values[field.id]"
                class="mt-2 w-full rounded-lg border border-slate-300 p-3"
              />
            </label>
          </div>
        </div>
        <p v-else class="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
          Choose a category and subcategory to load both inherited and subcategory-specific attributes.
        </p>
      </section>

      <aside class="h-fit rounded-2xl bg-slate-950 p-6 text-white">
        <h2 class="text-xl font-black">Publishing</h2>
        <p class="mt-2 text-sm text-slate-400">
          A product must be linked to a subcategory before it can be published.
        </p>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="mt-6 w-full rounded-xl bg-teal-500 px-5 py-3 font-bold disabled:opacity-60"
        >
          {{ isSubmitting ? 'Saving…' : 'Save product' }}
        </button>
      </aside>
    </form>
  </div>
</template>
