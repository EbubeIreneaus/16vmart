<script setup lang="ts">
import type { AttributeKey, Category } from '~/types/api'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const router = useRouter()
const storeSlug = String(route.params.store)
const { api } = useApi()

const isSubmitting = ref(false)
const isLoadingAttributes = ref(false)

const {
  fields: errorFields,
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

const { data: storeCategories } = await useAsyncData(
  `vendor-cats-${storeSlug}`,
  () => api<Category[]>(`/store/${storeSlug}/cat/all`),
  { default: () => [] }
)

const selectedCategoryId = ref<number | null>(null)
const selectedSubcategoryId = ref<number | null>(null)

const childCategories = computed(() => {
  if (!selectedCategoryId.value) return []
  const parent = (storeCategories.value || []).find(c => c.id === selectedCategoryId.value)
  return parent?.sub_categories || []
})

const fields = ref<AttributeKey[]>([])
const values = reactive<Record<number, any>>({})

watch([selectedCategoryId, selectedSubcategoryId], async ([catId, subCatId]) => {
  const targetCatId = subCatId || catId
  if (!targetCatId) {
    fields.value = []
    return
  }

  isLoadingAttributes.value = true
  try {
    const fetchedAttrs = await api<AttributeKey[]>(`/store/${storeSlug}/cat/attr/${targetCatId}`)
    fields.value = fetchedAttrs || []
    
    for (const attr of fields.value) {
      if (values[attr.id] === undefined) {
        if (attr.form_type === 'boolean') {
          values[attr.id] = false
        } else if (attr.form_type === 'multiple') {
          values[attr.id] = []
        } else {
          values[attr.id] = ''
        }
      }
    }
  } catch (err) {
    console.error('Failed to load attributes', err)
    fields.value = []
  } finally {
    isLoadingAttributes.value = false
  }
})

const form = reactive({
  name: '',
  price: 0,
  description: '',
  condition: 'brand new' as 'brand new' | 'used',
  available: true,
})

function onCategoryChange() {
  selectedSubcategoryId.value = null
}

async function saveProduct() {
  clearErrors()

  const catId = selectedSubcategoryId.value || selectedCategoryId.value
  if (!catId) {
    setError('Please select a product category.')
    return
  }

  isSubmitting.value = true

  try {
    const attributesPayload = fields.value
      .filter(f => values[f.id] !== undefined && values[f.id] !== null && values[f.id] !== '')
      .map(f => ({
        attribute_id: f.id,
        value: values[f.id],
      }))

    const response = await api<{ success: boolean; product_id: string }>(
      `/store/${storeSlug}/products/`,
      {
        method: 'POST',
        body: {
          name: form.name.trim(),
          price: form.price,
          description: form.description.trim(),
          condition: form.condition,
          available: form.available,
          category_id: Number(catId),
          attributes: attributesPayload,
        },
      }
    )

    if (response?.product_id) {
      await router.push(`/vendor/${storeSlug}/products/${response.product_id}/images`)
    } else {
      await router.push(`/vendor/${storeSlug}/products`)
    }
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
      <div>
        <p class="text-xs font-black uppercase tracking-widest text-teal-700">Catalog &bull; Step 1 of 2</p>
        <h1 class="mt-1 text-3xl font-black text-slate-900">Add Product Details</h1>
        <p class="mt-1 text-sm text-slate-500">
          Enter product information and category specification attributes. Product images are uploaded in Step 2.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <span class="inline-flex items-center rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-800">
          Step 1: Product Info
        </span>
        <span class="text-slate-300">&rarr;</span>
        <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-400">
          Step 2: Upload Images
        </span>
      </div>
    </div>

    <form class="mt-8 grid gap-7 lg:grid-cols-[1fr_300px]" @submit.prevent="saveProduct">
      <section class="space-y-6 rounded-2xl bg-white p-6 sm:p-8 shadow-sm ring-1 ring-slate-200">
        <div v-if="errorMessage" class="rounded-xl bg-rose-50 p-4 text-sm font-semibold text-rose-700 border border-rose-200">
          {{ errorMessage }}
        </div>

        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold text-slate-800">
            Category <span class="text-rose-500">*</span>
            <select
              v-model="selectedCategoryId"
              required
              class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
              @change="onCategoryChange"
            >
              <option :value="null" disabled>Select category</option>
              <option v-for="cat in storeCategories" :key="cat.id" :value="cat.id">
                {{ cat.name.toUpperCase() }}
              </option>
            </select>
          </label>

          <label class="text-sm font-bold text-slate-800">
            Subcategory
            <select
              v-model="selectedSubcategoryId"
              class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none disabled:bg-slate-50 disabled:text-slate-400"
              :disabled="!selectedCategoryId || !childCategories.length"
            >
              <option :value="null">
                {{ childCategories.length ? 'Select subcategory (optional)' : 'No subcategories' }}
              </option>
              <option v-for="sub in childCategories" :key="sub.id" :value="sub.id">
                {{ sub.name.toUpperCase() }}
              </option>
            </select>
          </label>
        </div>

        <!-- Basic Product Information -->
        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold text-slate-800">
            Product Name <span class="text-rose-500">*</span>
            <input
              v-model="form.name"
              required
              class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
              placeholder="e.g. Wireless Noise Canceling Headphones"
            />
          </label>

          <label class="text-sm font-bold text-slate-800">
            Price ($) <span class="text-rose-500">*</span>
            <input
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0"
              required
              class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
              placeholder="0.00"
            />
          </label>
        </div>

        <div class="grid gap-5 md:grid-cols-2">
          <label class="text-sm font-bold text-slate-800">
            Condition
            <select v-model="form.condition" class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none">
              <option value="brand new">Brand New</option>
              <option value="used">Used</option>
            </select>
          </label>

          <label class="text-sm font-bold text-slate-800 flex items-center gap-3 pt-6">
            <input
              v-model="form.available"
              type="checkbox"
              class="h-5 w-5 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
            />
            <span>Available for Sale</span>
          </label>
        </div>

        <label class="block text-sm font-bold text-slate-800">
          Product Description <span class="text-rose-500">*</span>
          <textarea
            v-model="form.description"
            required
            rows="4"
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
            placeholder="Detailed description of features, specifications, and warranty..."
          />
        </label>

        <!-- Dynamic Category Attributes Section -->
        <div class="border-t border-slate-200 pt-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-black text-slate-900">Category Attributes</h2>
              <p class="text-xs text-slate-500">Attributes required or configured for the chosen category.</p>
            </div>
            <span v-if="isLoadingAttributes" class="text-xs font-bold text-teal-700 animate-pulse">
              Loading category attributes...
            </span>
            <span v-else-if="fields.length" class="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full">
              {{ fields.length }} attribute{{ fields.length > 1 ? 's' : '' }}
            </span>
          </div>

          <!-- Dynamic Input Fields Rendering -->
          <div v-if="fields.length" class="mt-5 grid gap-5 md:grid-cols-2">
            <div v-for="field in fields" :key="field.id" class="text-sm font-bold text-slate-800">
              <label class="block">
                {{ field.name }}
                <span v-if="field.required" class="text-rose-500">*</span>
              </label>

              <!-- Select Input -->
              <template v-if="field.form_type === 'select'">
                <select
                  v-model="values[field.id]"
                  :required="field.required"
                  class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
                >
                  <option value="" disabled>Select {{ field.name }}</option>
                  <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </template>

              <!-- Radio Input -->
              <template v-else-if="field.form_type === 'radio'">
                <div class="mt-2 space-y-2">
                  <label v-for="opt in field.options" :key="opt" class="flex items-center gap-2 font-normal text-sm cursor-pointer">
                    <input
                      v-model="values[field.id]"
                      type="radio"
                      :name="`attr-${field.id}`"
                      :value="opt"
                      class="text-teal-600"
                    />
                    <span>{{ opt }}</span>
                  </label>
                </div>
              </template>

              <!-- Multiple Select Input -->
              <template v-else-if="field.form_type === 'multiple'">
                <select
                  v-model="values[field.id]"
                  multiple
                  class="mt-2 min-h-28 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
                >
                  <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>
                <p class="mt-1 text-[11px] text-slate-400 font-normal">Hold Ctrl / Cmd to select multiple items.</p>
              </template>

              <!-- Boolean Input (Checkbox) -->
              <template v-else-if="field.form_type === 'boolean'">
                <label class="mt-3 flex items-center gap-2 font-normal text-sm cursor-pointer">
                  <input
                    v-model="values[field.id]"
                    type="checkbox"
                    class="h-5 w-5 rounded border-slate-300 text-teal-600"
                  />
                  <span>Yes / True</span>
                </label>
              </template>

              <!-- Date Input -->
              <template v-else-if="field.form_type === 'date'">
                <input
                  v-model="values[field.id]"
                  type="date"
                  :required="field.required"
                  class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
                />
              </template>

              <!-- Number Input -->
              <template v-else-if="field.form_type === 'number'">
                <input
                  v-model.number="values[field.id]"
                  type="number"
                  :required="field.required"
                  class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
                />
              </template>

              <!-- Default Text Input -->
              <template v-else>
                <input
                  v-model="values[field.id]"
                  type="text"
                  :required="field.required"
                  class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
                  :placeholder="`Enter ${field.name.toLowerCase()}`"
                />
              </template>
            </div>
          </div>

          <div v-else-if="selectedCategoryId" class="mt-4 rounded-xl bg-slate-50 p-4 text-center text-sm text-slate-500 italic">
            No specific attributes configured for this category.
          </div>

          <div v-else class="mt-4 rounded-xl bg-amber-50/70 p-4 text-sm text-amber-800 border border-amber-200">
            Please select a category above to load category-specific attributes.
          </div>
        </div>
      </section>

      <!-- Sidebar Action -->
      <aside class="h-fit rounded-2xl bg-slate-900 p-6 text-white shadow-xl">
        <h2 class="text-xl font-black">Next Step</h2>
        <p class="mt-2 text-sm text-slate-300">
          Once product details are saved, you will proceed to Step 2 to upload high-resolution product images.
        </p>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="mt-6 w-full rounded-xl bg-teal-600 hover:bg-teal-500 py-3.5 text-sm font-bold text-white shadow-lg transition disabled:opacity-60 flex items-center justify-center gap-2"
        >
          <span>{{ isSubmitting ? 'Saving Product...' : 'Continue to Upload Images &rarr;' }}</span>
        </button>
      </aside>
    </form>
  </div>
</template>
