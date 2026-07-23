<script setup lang="ts">
import type { AdminCategory, FormType } from '~/types/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const route = useRoute()
const router = useRouter()
const { api } = useApi()

const slug = computed(() => route.params.slug as string)

const { data: category, pending, error, refresh } = await useAsyncData(
  `admin-category-${slug.value}`,
  () => api<AdminCategory>(`/admin/cat/${slug.value}`)
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

function isOptionType(type: FormType) {
  return ['select', 'multiple', 'radio'].includes(type)
}

function parseOptions(inputStr: string): string[] | null {
  if (!inputStr || !inputStr.trim()) return null
  const opts = inputStr.split(',').map(s => s.trim()).filter(Boolean)
  return opts.length > 0 ? opts : null
}

// Edit category modal state
const editModalOpen = ref(false)
const editName = ref('')
const editAttributes = ref<DraftAttribute[]>([])
const editSubCategories = ref<DraftSubCategory[]>([])
const editAttributeName = ref('')
const editAttributeType = ref<FormType>('text')
const editAttributeOptionsInput = ref('')
const isEditSubmitting = ref(false)

function openEditModal() {
  if (!category.value) return
  editName.value = category.value.name
  editAttributes.value = category.value.attributes ? category.value.attributes.map(a => ({
    name: a.name,
    required: a.required,
    form_type: a.form_type,
    options: a.options ? [...a.options] : null,
  })) : []
  editSubCategories.value = category.value.sub_categories ? category.value.sub_categories.map(s => ({
    name: s.name,
    attributes: s.attributes ? s.attributes.map(sa => ({
      name: sa.name,
      required: sa.required,
      form_type: sa.form_type,
      options: sa.options ? [...sa.options] : null,
    })) : [],
  })) : []
  editModalOpen.value = true
}

function addEditAttribute() {
  if (!editAttributeName.value.trim()) return
  const opts = isOptionType(editAttributeType.value)
    ? parseOptions(editAttributeOptionsInput.value)
    : null

  editAttributes.value.push({
    name: editAttributeName.value.trim(),
    required: true,
    form_type: editAttributeType.value,
    options: opts,
  })

  editAttributeName.value = ''
  editAttributeOptionsInput.value = ''
}

function removeEditAttribute(index: number) {
  editAttributes.value.splice(index, 1)
}

async function updateCategory() {
  if (!category.value) return
  clearErrors()
  isEditSubmitting.value = true

  try {
    await api(`/admin/cat/${category.value.id}`, {
      method: 'PUT',
      body: {
        name: editName.value.trim(),
        attributes: editAttributes.value,
        sub_categories: editSubCategories.value,
      },
    })
    editModalOpen.value = false
    // Clear edit query parameter if present
    if (route.query.edit) {
      router.replace({ query: {} })
    }
    await refresh()
  } catch (err) {
    setError(err)
  } finally {
    isEditSubmitting.value = false
  }
}

// Auto open edit modal if query has edit=true
watch(category, (val) => {
  if (val && route.query.edit === 'true') {
    openEditModal()
  }
}, { immediate: true })

// Delete category modal state
const deleteModalOpen = ref(false)
const isDeleteSubmitting = ref(false)

async function deleteCategory() {
  if (!category.value) return
  isDeleteSubmitting.value = true

  try {
    await api(`/admin/cat/${category.value.id}`, {
      method: 'DELETE',
    })
    deleteModalOpen.value = false
    router.push('/admin/categories')
  } catch (err) {
    setError(err)
  } finally {
    isDeleteSubmitting.value = false
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Navigation Breadcrumb -->
    <div class="mb-6 flex items-center gap-2 text-sm text-slate-500">
      <NuxtLink to="/admin/categories" class="hover:text-teal-700 font-medium transition flex items-center gap-1">
        &larr; Categories
      </NuxtLink>
      <span>/</span>
      <span class="font-bold text-slate-800 capitalize">{{ category?.name || slug }}</span>
    </div>

    <!-- Loading & Error States -->
    <div v-if="pending" class="py-12 text-center text-slate-500">
      Loading category details...
    </div>

    <div v-else-if="error || !category" class="rounded-2xl bg-rose-50 p-8 text-center border border-rose-200">
      <h2 class="text-xl font-bold text-rose-800">Category not found</h2>
      <p class="mt-2 text-sm text-rose-600">The requested category standard does not exist or has been deleted.</p>
      <NuxtLink to="/admin/categories" class="mt-4 inline-block rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white">
        Return to Categories
      </NuxtLink>
    </div>

    <div v-else>
      <!-- Page Header -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-3xl sm:text-4xl font-black text-slate-900 capitalize">{{ category.name }}</h1>
            <span class="rounded-md bg-teal-100 px-3 py-1 text-xs font-mono font-bold text-teal-800">
              /{{ category.slug }}
            </span>
          </div>
          <p class="mt-1 text-sm text-slate-500">Detailed view of category attributes and subcategories.</p>
        </div>

        <div class="flex items-center gap-3">
          <button
            class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-bold text-slate-700 hover:bg-slate-50 shadow-xs transition"
            @click="openEditModal"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Category
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200 px-4 py-2.5 text-sm font-bold text-rose-700 hover:bg-rose-100 shadow-xs transition"
            @click="deleteModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="mt-8 grid gap-8 lg:grid-cols-3">
        <!-- Left 2 Columns: Attributes & Subcategories -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Section 1: Attributes List -->
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/80">
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
              <h2 class="text-lg font-black text-slate-900">Attributes & Input Types</h2>
              <span class="text-xs font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md">
                {{ category.attributes?.length || 0 }} defined
              </span>
            </div>

            <div v-if="category.attributes?.length" class="mt-4 divide-y divide-slate-100">
              <div v-for="attr in category.attributes" :key="attr.id" class="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-900 text-sm capitalize">{{ attr.name }}</span>
                    <span
                      class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider"
                      :class="attr.required ? 'text-teal-700 bg-teal-50' : 'text-slate-500'"
                    >
                      {{ attr.required ? 'Required' : 'Optional' }}
                    </span>
                  </div>
                  <!-- Options listing if present -->
                  <div v-if="attr.options?.length" class="mt-1.5 flex flex-wrap items-center gap-1.5">
                    <span class="text-xs font-medium text-slate-500">Allowed Options:</span>
                    <span
                      v-for="(opt, oIdx) in attr.options"
                      :key="oIdx"
                      class="rounded-md bg-slate-100 border border-slate-200 px-2 py-0.5 text-xs text-slate-700 font-mono"
                    >
                      {{ opt }}
                    </span>
                  </div>
                  <div v-else-if="isOptionType(attr.form_type)" class="mt-1 text-xs text-amber-600 font-medium">
                    No explicit options defined for {{ attr.form_type }}.
                  </div>
                </div>

                <div class="shrink-0">
                  <span class="inline-block rounded-lg bg-teal-700/10 px-3 py-1 text-xs font-bold text-teal-800 uppercase tracking-wider">
                    {{ attr.form_type }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="mt-4 py-6 text-center text-sm text-slate-400 italic">
              No shared attributes defined for this category.
            </div>
          </div>

          <!-- Section 2: Subcategories List -->
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/80">
            <div class="flex items-center justify-between border-b border-slate-100 pb-4">
              <h2 class="text-lg font-black text-slate-900">Subcategories</h2>
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
                {{ category.sub_categories?.length || 0 }} subcategories
              </span>
            </div>

            <div v-if="category.sub_categories?.length" class="mt-4 space-y-4">
              <div
                v-for="sub in category.sub_categories"
                :key="sub.id"
                class="rounded-xl border border-slate-200 p-4 bg-slate-50/50 hover:bg-white transition"
              >
                <div class="flex items-center justify-between">
                  <h3 class="font-bold text-slate-900 text-base capitalize">{{ sub.name }}</h3>
                  <span class="text-xs font-mono text-slate-400">/{{ sub.slug }}</span>
                </div>

                <div class="mt-3">
                  <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Subcategory Unique Attributes</p>
                  <div v-if="sub.attributes?.length" class="mt-2 flex flex-wrap gap-2">
                    <div
                      v-for="sa in sub.attributes"
                      :key="sa.id"
                      class="rounded-lg bg-white border border-slate-200 px-3 py-1.5 text-xs text-slate-700 font-medium"
                    >
                      <span class="font-bold text-slate-900">{{ sa.name }}</span>
                      <span class="ml-1 text-[10px] uppercase font-bold text-teal-700 bg-teal-50 px-1 py-0.5 rounded">
                        {{ sa.form_type }}
                      </span>
                      <span v-if="sa.options?.length" class="ml-1 text-[10px] text-slate-500">
                        [{{ sa.options.join(', ') }}]
                      </span>
                    </div>
                  </div>
                  <p v-else class="mt-1 text-xs text-slate-400 italic">No unique sub-attributes defined.</p>
                </div>
              </div>
            </div>

            <div v-else class="mt-4 py-6 text-center text-sm text-slate-400 italic">
              No subcategories registered under {{ category.name }}.
            </div>
          </div>
        </div>

        <!-- Right 1 Column: Summary Card -->
        <div class="space-y-6">
          <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/80">
            <h2 class="text-lg font-black text-slate-900 border-b border-slate-100 pb-3">Category Information</h2>
            
            <dl class="mt-4 space-y-4 text-sm">
              <div>
                <dt class="text-xs font-bold uppercase tracking-wider text-slate-400">Category Name</dt>
                <dd class="mt-0.5 font-bold text-slate-900 text-base capitalize">{{ category.name }}</dd>
              </div>
              <div>
                <dt class="text-xs font-bold uppercase tracking-wider text-slate-400">URL Slug</dt>
                <dd class="mt-0.5 font-mono text-slate-700 text-xs bg-slate-100 p-1.5 rounded-md inline-block">
                  {{ category.slug }}
                </dd>
              </div>
              <div>
                <dt class="text-xs font-bold uppercase tracking-wider text-slate-400">Database ID</dt>
                <dd class="mt-0.5 font-semibold text-slate-700">{{ category.id }}</dd>
              </div>
              <div>
                <dt class="text-xs font-bold uppercase tracking-wider text-slate-400">Subcategories Count</dt>
                <dd class="mt-0.5 font-semibold text-slate-700">{{ category.sub_categories?.length || 0 }}</dd>
              </div>
              <div>
                <dt class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Attributes</dt>
                <dd class="mt-0.5 font-semibold text-slate-700">{{ category.attributes?.length || 0 }}</dd>
              </div>
            </dl>

            <div class="mt-6 border-t border-slate-100 pt-4">
              <button
                class="w-full rounded-xl bg-teal-700 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 transition"
                @click="openEditModal"
              >
                Edit Category
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Category Modal -->
    <div v-if="editModalOpen" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs overflow-y-auto">
      <form
        class="my-8 max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 sm:p-8 shadow-2xl"
        @submit.prevent="updateCategory"
      >
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <h2 class="text-2xl font-black text-slate-900">Edit Category</h2>
          <button type="button" class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" @click="editModalOpen = false">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p v-if="errorMessage" class="mt-4 rounded-xl bg-rose-50 p-3 text-sm font-semibold text-rose-700 border border-rose-200">
          {{ errorMessage }}
        </p>

        <label class="mt-5 block text-sm font-bold text-slate-800">
          Category Name
          <input
            v-model="editName"
            required
            class="mt-2 w-full rounded-xl border border-slate-300 p-3 text-sm focus:border-teal-600 outline-none"
          />
        </label>

        <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50/50 p-4">
          <h3 class="font-black text-slate-900 text-sm">Attributes</h3>

          <div class="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center">
            <input
              v-model="editAttributeName"
              class="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white p-2.5 text-sm outline-none focus:border-teal-600"
              placeholder="Attribute name"
            />
            <select
              v-model="editAttributeType"
              class="rounded-lg border border-slate-300 bg-white p-2.5 text-sm outline-none focus:border-teal-600"
            >
              <option v-for="type in ['text','select','multiple','radio','date','boolean','number']" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>

          <div v-if="isOptionType(editAttributeType)" class="mt-2">
            <input
              v-model="editAttributeOptionsInput"
              class="w-full rounded-lg border border-teal-300 bg-teal-50/40 p-2.5 text-sm outline-none focus:border-teal-600"
              placeholder="Options separated by comma (e.g. Red, Blue, Green)"
            />
          </div>

          <button
            type="button"
            class="mt-3 rounded-lg bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition"
            @click="addEditAttribute"
          >
            + Add Attribute
          </button>

          <div v-if="editAttributes.length" class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="(attr, i) in editAttributes"
              :key="i"
              class="inline-flex items-center gap-1.5 rounded-full bg-teal-100 px-3 py-1 text-xs font-bold text-teal-900"
            >
              {{ attr.name }} ({{ attr.form_type }})
              <span v-if="attr.options?.length" class="text-[10px] text-teal-700">[{{ attr.options.join(', ') }}]</span>
              <button type="button" class="ml-1 text-teal-700 hover:text-rose-600 font-bold" @click="removeEditAttribute(i)">×</button>
            </span>
          </div>
        </div>

        <div class="mt-7 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-slate-300 px-5 py-3 text-sm font-bold text-slate-700 hover:bg-slate-100"
            @click="editModalOpen = false"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isEditSubmitting"
            class="rounded-xl bg-teal-700 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 disabled:opacity-60"
          >
            {{ isEditSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Delete Category Modal -->
    <div v-if="deleteModalOpen" class="fixed inset-0 z-30 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-xs">
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="text-xl font-black text-slate-900">Delete Category</h3>
        <p class="mt-2 text-sm text-slate-600">
          Are you sure you want to delete <strong class="text-slate-900">{{ category?.name }}</strong>?
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
