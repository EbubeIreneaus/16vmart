<script setup lang="ts">
import type { Category, FormType } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const { api } = useApi()
const router = useRouter()

const { data: categories, refresh } = await useAsyncData('admin-categories', () =>
  api<Category[]>('/admin/cat/all'),
  { default: () => [] }
)

const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

interface DraftAttribute {
  name: string
  required: boolean
  form_type: FormType
  options: string[] | null
}

interface DraftSubCategory {
  name: string
  attributes: DraftAttribute[]
}

// Create Category Modal state
const open = ref(false)
const name = ref('')
const isSubmitting = ref(false)

// New attribute form state
const attributeName = ref('')
const attributeType = ref<FormType>('text')
const attributeOptionsInput = ref('')
const draftAttributes = ref<DraftAttribute[]>([])

// New subcategory form state
const subCategoryName = ref('')
const subCategoryAttrInputs = ref<{ name: string; type: FormType; options: string }[]>([])
const draftSubCategories = ref<DraftSubCategory[]>([])

function isOptionType(type: FormType) {
  return ['select', 'multiple', 'radio'].includes(type)
}

function parseOptions(inputStr: string): string[] | null {
  if (!inputStr || !inputStr.trim()) return null
  const opts = inputStr.split(',').map(s => s.trim()).filter(Boolean)
  return opts.length > 0 ? opts : null
}

function addAttribute() {
  if (!attributeName.value.trim()) return
  const opts = isOptionType(attributeType.value)
    ? parseOptions(attributeOptionsInput.value)
    : null

  draftAttributes.value.push({
    name: attributeName.value.trim(),
    required: true,
    form_type: attributeType.value,
    options: opts,
  })

  attributeName.value = ''
  attributeOptionsInput.value = ''
}

function removeAttribute(index: number) {
  draftAttributes.value.splice(index, 1)
}

function addSubCategory() {
  if (!subCategoryName.value.trim()) return
  
  const subAttrs: DraftAttribute[] = subCategoryAttrInputs.value
    .filter(a => a.name.trim())
    .map(a => ({
      name: a.name.trim(),
      required: true,
      form_type: a.type,
      options: isOptionType(a.type) ? parseOptions(a.options) : null,
    }))

  draftSubCategories.value.push({
    name: subCategoryName.value.trim(),
    attributes: subAttrs,
  })

  subCategoryName.value = ''
  subCategoryAttrInputs.value = []
}

function addSubCatAttrField() {
  subCategoryAttrInputs.value.push({ name: '', type: 'text', options: '' })
}

function removeSubCatAttrField(index: number) {
  subCategoryAttrInputs.value.splice(index, 1)
}

function removeSubCategory(index: number) {
  draftSubCategories.value.splice(index, 1)
}

async function createCategory() {
  clearErrors()
  if (!name.value.trim()) return

  isSubmitting.value = true
  try {
    await api('/admin/cat/create-category', {
      method: 'POST',
      body: {
        name: name.value.trim(),
        attributes: draftAttributes.value.length > 0 ? draftAttributes.value : null,
        sub_categories: draftSubCategories.value.length > 0 ? draftSubCategories.value : null,
      },
    })
    open.value = false
    resetCreateForm()
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isSubmitting.value = false
  }
}

function resetCreateForm() {
  name.value = ''
  attributeName.value = ''
  attributeType.value = 'text'
  attributeOptionsInput.value = ''
  draftAttributes.value = []
  subCategoryName.value = ''
  subCategoryAttrInputs.value = []
  draftSubCategories.value = []
}

function navigateToEdit(slug: string) {
  router.push(`/admin/categories/${slug}?edit=true`)
}

// Delete Category Confirmation Modal state
const deleteModalOpen = ref(false)
const deletingCategory = ref<Category | null>(null)
const isDeleteSubmitting = ref(false)

function confirmDelete(category: Category) {
  deletingCategory.value = category
  deleteModalOpen.value = true
}

async function deleteCategory() {
  if (!deletingCategory.value) return
  isDeleteSubmitting.value = true

  try {
    await api(`/admin/cat/${deletingCategory.value.id}`, {
      method: 'DELETE',
    })
    deleteModalOpen.value = false
    deletingCategory.value = null
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isDeleteSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
      <div>
        <p class="text-xs font-black uppercase tracking-widest text-teal-700">Product Taxonomy</p>
        <h1 class="mt-1 text-3xl sm:text-4xl font-black text-slate-900">Categories</h1>
        <p class="mt-1 text-sm text-slate-500">Overview of top-level product categories.</p>
      </div>
      <button
        class="inline-flex items-center gap-2 rounded-xl bg-teal-700 px-5 py-3 font-bold text-white shadow-md hover:bg-teal-800 transition"
        @click="open = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New category
      </button>
    </div>

    <!-- Category Grid -->
    <div class="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="category in categories"
        :key="category.id"
        class="group relative flex flex-col justify-between rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/80 hover:shadow-md hover:ring-teal-500/50 transition duration-200"
      >
        <div>
          <!-- Header & Info -->
          <div class="flex items-start justify-between gap-4">
            <div>
              <NuxtLink
                :to="`/admin/categories/${category.slug}`"
                class="text-xl font-black text-slate-900 hover:text-teal-700 transition flex items-center gap-2 capitalize"
              >
                {{ category.name }}
              </NuxtLink>
              <span class="inline-block mt-1.5 rounded-md bg-slate-100 px-2 py-0.5 text-xs font-mono font-bold text-slate-500">
                /{{ category.slug }}
              </span>
            </div>

            <span class="text-xs font-mono font-bold text-slate-400">
              #{{ category.id }}
            </span>
          </div>
        </div>

        <!-- 3 Supported Actions: View Details, Edit, Delete -->
        <div class="mt-8 border-t border-slate-100 pt-4 flex items-center justify-between gap-2">
          <NuxtLink
            :to="`/admin/categories/${category.slug}`"
            class="inline-flex items-center gap-1 text-xs font-bold text-teal-700 hover:text-teal-900 transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            View Details
          </NuxtLink>

          <div class="flex items-center gap-1">
            <button
              title="Edit category"
              class="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-bold text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition"
              @click="navigateToEdit(category.slug)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
            <button
              title="Delete category"
              class="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-bold text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition"
              @click="confirmDelete(category)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </button>
          </div>
        </div>
      </article>
    </div>

    <!-- Create Modal -->
    <div v-if="open" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs overflow-y-auto">
      <form
        class="my-8 max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 sm:p-8 shadow-2xl"
        @submit.prevent="createCategory"
      >
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <h2 class="text-2xl font-black text-slate-900">Create Category</h2>
          <button type="button" class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" @click="open = false">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p v-if="errorMessage" class="mt-4 rounded-xl bg-rose-50 p-3 text-sm font-semibold text-rose-700 border border-rose-200">
          {{ errorMessage }}
        </p>

        <!-- Category Name -->
        <label class="mt-5 block text-sm font-bold text-slate-800">
          Category Name <span class="text-rose-500">*</span>
          <input
            v-model="name"
            required
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20 outline-none"
            placeholder="e.g. Electronics"
          />
        </label>

        <!-- Shared Attributes Section -->
        <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50/50 p-4">
          <h3 class="font-black text-slate-900 text-sm">Shared Attributes</h3>
          <p class="mt-0.5 text-xs text-slate-500">Attributes added here will be inherited by all subcategories.</p>

          <div class="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
            <input
              v-model="attributeName"
              class="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white p-2.5 text-sm outline-none focus:border-teal-600"
              placeholder="Attribute name (e.g. Brand)"
            />
            <select
              v-model="attributeType"
              class="rounded-lg border border-slate-300 bg-white p-2.5 text-sm outline-none focus:border-teal-600"
            >
              <option v-for="type in ['text','select','multiple','radio','date','boolean','number']" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>

          <!-- Options Input Field for Select, Multiple, Radio -->
          <div v-if="isOptionType(attributeType)" class="mt-2">
            <input
              v-model="attributeOptionsInput"
              class="w-full rounded-lg border border-teal-300 bg-teal-50/40 p-2.5 text-sm outline-none focus:border-teal-600"
              placeholder="Enter options separated by comma (e.g. Red, Blue, Green)"
            />
            <p class="mt-1 text-[11px] text-teal-700">Separate multiple options with commas.</p>
          </div>

          <button
            type="button"
            class="mt-3 rounded-lg bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition"
            @click="addAttribute"
          >
            + Add Attribute
          </button>

          <!-- Draft Attributes Tag List -->
          <div v-if="draftAttributes.length" class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="(attr, i) in draftAttributes"
              :key="i"
              class="inline-flex items-center gap-1.5 rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-900"
            >
              {{ attr.name }} ({{ attr.form_type }})
              <span v-if="attr.options?.length" class="text-[10px] text-teal-700">[{{ attr.options.join(', ') }}]</span>
              <button type="button" class="ml-1 text-teal-700 hover:text-rose-600 font-bold" @click="removeAttribute(i)">×</button>
            </span>
          </div>
        </div>

        <!-- Subcategories Section -->
        <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50/50 p-4">
          <h3 class="font-black text-slate-900 text-sm">Add Subcategories</h3>
          <p class="mt-0.5 text-xs text-slate-500">Define nested subcategories during creation.</p>

          <div class="mt-3 space-y-3">
            <div class="flex gap-2">
              <input
                v-model="subCategoryName"
                class="flex-1 rounded-lg border border-slate-300 bg-white p-2.5 text-sm outline-none focus:border-teal-600"
                placeholder="Subcategory name (e.g. Smartphones)"
              />
              <button
                type="button"
                class="rounded-lg bg-teal-700 px-4 py-2 text-xs font-bold text-white hover:bg-teal-800 transition"
                @click="addSubCategory"
              >
                Add Subcategory
              </button>
            </div>

            <!-- Subcategory Unique Attributes Inputs -->
            <div class="space-y-2">
              <div v-for="(subAttr, idx) in subCategoryAttrInputs" :key="idx" class="p-2.5 rounded-lg bg-white border border-slate-200 space-y-2">
                <div class="flex gap-2 items-center">
                  <input
                    v-model="subAttr.name"
                    class="flex-1 rounded-md border border-slate-300 p-2 text-xs outline-none"
                    placeholder="Sub-attribute name (e.g. Storage)"
                  />
                  <select v-model="subAttr.type" class="rounded-md border border-slate-300 p-2 text-xs outline-none">
                    <option v-for="t in ['text','select','multiple','radio','date','boolean','number']" :key="t" :value="t">{{ t }}</option>
                  </select>
                  <button type="button" class="text-rose-500 font-bold text-xs" @click="removeSubCatAttrField(idx)">Remove</button>
                </div>
                <input
                  v-if="isOptionType(subAttr.type)"
                  v-model="subAttr.options"
                  class="w-full rounded-md border border-teal-200 bg-teal-50/30 p-2 text-xs outline-none"
                  placeholder="Options comma-separated (e.g. 64GB, 128GB, 256GB)"
                />
              </div>

              <button
                type="button"
                class="text-xs font-bold text-teal-700 hover:text-teal-900 inline-flex items-center gap-1"
                @click="addSubCatAttrField"
              >
                + Add Unique Attribute for Subcategory
              </button>
            </div>
          </div>

          <!-- Draft Subcategories List -->
          <div v-if="draftSubCategories.length" class="mt-4 space-y-2">
            <div
              v-for="(sub, i) in draftSubCategories"
              :key="i"
              class="flex items-center justify-between rounded-lg bg-white p-3 border border-slate-200 text-xs"
            >
              <div>
                <span class="font-bold text-slate-900">{{ sub.name }}</span>
                <span v-if="sub.attributes.length" class="ml-2 text-slate-500">
                  ({{ sub.attributes.map(a => a.name).join(', ') }})
                </span>
              </div>
              <button type="button" class="text-rose-600 font-bold hover:underline" @click="removeSubCategory(i)">
                Remove
              </button>
            </div>
          </div>
        </div>

        <div class="mt-7 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-slate-300 px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-100"
            @click="open = false"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="rounded-xl bg-teal-700 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 disabled:opacity-60"
          >
            {{ isSubmitting ? 'Creating...' : 'Create Category' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModalOpen" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="text-xl font-black text-slate-900">Delete Category</h3>
        <p class="mt-2 text-sm text-slate-600">
          Are you sure you want to delete <strong class="text-slate-900">{{ deletingCategory?.name }}</strong>?
          This action will also remove associated subcategories and attributes.
        </p>

        <div class="mt-6 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-bold text-slate-700 hover:bg-slate-100"
            @click="deleteModalOpen = false"
          >
            Cancel
          </button>
          <button
            type="button"
            :disabled="isDeleteSubmitting"
            class="rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-60"
            @click="deleteCategory"
          >
            {{ isDeleteSubmitting ? 'Deleting...' : 'Delete Category' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
