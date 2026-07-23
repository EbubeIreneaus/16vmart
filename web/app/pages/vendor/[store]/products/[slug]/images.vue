<script setup lang="ts">
import type { Image } from '~/types/api'

definePageMeta({ layout: 'vendor', middleware: 'seller' })

const route = useRoute()
const router = useRouter()
const storeSlug = String(route.params.store)
const slug = String(route.params.slug)
const { api } = useApi()

const isUploading = ref(false)
const deletingImageName = ref<string | null>(null)
const selectedFiles = ref<File[]>([])
const previewUrls = ref<string[]>([])

const {
  message: errorMessage,
  setError,
  clearErrors,
} = useGetAPIFormError()

// Fetch current product details & images
const { data: product, refresh } = await useAsyncData(
  `vendor-product-images-${slug}`,
  () => api<{ name: string; slug: string; images?: Image[] }>(`/store/${storeSlug}/products/${slug}`)
)

function onFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

function onDrop(event: DragEvent) {
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

function addFiles(files: File[]) {
  const imageFiles = files.filter(f => f.type.startsWith('image/'))
  selectedFiles.value = [...selectedFiles.value, ...imageFiles]
  
  // Generate preview URLs
  previewUrls.value = selectedFiles.value.map(file => URL.createObjectURL(file))
}

function removeSelectedFile(index: number) {
  selectedFiles.value.splice(index, 1)
  previewUrls.value.splice(index, 1)
}

async function uploadImages() {
  if (!selectedFiles.value.length) return
  clearErrors()
  isUploading.value = true

  try {
    const formData = new FormData()
    selectedFiles.value.forEach(file => {
      formData.append('files', file)
    })

    await api(`/store/${storeSlug}/products/image/${slug}`, {
      method: 'PATCH',
      body: formData,
    })

    selectedFiles.value = []
    previewUrls.value = []
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    isUploading.value = false
  }
}

async function deleteImage(imageName: string) {
  if (!imageName) return
  deletingImageName.value = imageName
  clearErrors()

  try {
    await api(`/store/${storeSlug}/products/image/${imageName}/${slug}`, {
      method: 'DELETE',
    })
    await refresh()
  } catch (error) {
    setError(error)
  } finally {
    deletingImageName.value = null
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6">
    <!-- Header with Step Indicator -->
    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-6">
      <div>
        <p class="text-xs font-black uppercase tracking-widest text-teal-700">Catalog &bull; Step 2 of 2</p>
        <h1 class="mt-1 text-3xl font-black text-slate-900 capitalize">
          Upload Images &mdash; {{ product?.name || slug }}
        </h1>
        <p class="mt-1 text-sm text-slate-500">
          Upload high quality product images. Images will be processed and displayed in your store catalog.
        </p>
      </div>

      <NuxtLink
        :to="`/vendor/${storeSlug}/products`"
        class="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-bold text-white shadow-md hover:bg-slate-800 transition"
      >
        Finish &amp; View Catalog
      </NuxtLink>
    </div>

    <div class="mt-8 space-y-8">
      <p v-if="errorMessage" class="rounded-xl bg-rose-50 p-4 text-sm font-semibold text-rose-700 border border-rose-200">
        {{ errorMessage }}
      </p>

      <!-- Dropzone Upload Box -->
      <div
        class="group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-white p-8 text-center hover:border-teal-500 hover:bg-teal-50/20 transition cursor-pointer"
        @dragover.prevent
        @drop.prevent="onDrop"
      >
        <input
          type="file"
          multiple
          accept="image/*"
          class="absolute inset-0 opacity-0 cursor-pointer"
          @change="onFileSelect"
        />

        <div class="rounded-full bg-teal-50 p-4 text-teal-700 group-hover:scale-110 transition">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>

        <h3 class="mt-4 text-lg font-black text-slate-900">Drag &amp; drop product images here</h3>
        <p class="mt-1 text-sm text-slate-500">or click to browse from your device (PNG, JPG, WEBP, up to 10MB each)</p>
      </div>

      <!-- Selected Files Preview before Upload -->
      <div v-if="selectedFiles.length" class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <h3 class="text-base font-black text-slate-900">Selected for Upload ({{ selectedFiles.length }})</h3>
          <button
            type="button"
            :disabled="isUploading"
            class="rounded-xl bg-teal-700 px-5 py-2.5 text-sm font-bold text-white shadow-md hover:bg-teal-800 disabled:opacity-60 transition"
            @click="uploadImages"
          >
            {{ isUploading ? 'Uploading to Server...' : 'Upload Images Now' }}
          </button>
        </div>

        <div class="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          <div v-for="(url, idx) in previewUrls" :key="idx" class="relative group rounded-xl overflow-hidden border border-slate-200 bg-slate-50">
            <img :src="url" class="w-full h-32 object-cover" />
            <div class="p-2 text-xs truncate font-medium text-slate-700">
              {{ selectedFiles[idx]?.name }}
            </div>
            <button
              type="button"
              class="absolute top-2 right-2 rounded-full bg-slate-900/80 p-1.5 text-white hover:bg-rose-600 transition"
              @click="removeSelectedFile(idx)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Uploaded Images Gallery -->
      <div class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 class="text-base font-black text-slate-900 border-b border-slate-100 pb-4">
          Uploaded Product Images ({{ product?.images?.length || 0 }})
        </h3>

        <div v-if="product?.images?.length" class="mt-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          <div
            v-for="img in product.images"
            :key="img.src"
            class="group relative rounded-xl overflow-hidden border border-slate-200 bg-slate-50 shadow-xs"
          >
            <img :src="img.src" :alt="img.alt || product.name" class="w-full h-36 object-cover" />
            <div class="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center p-2">
              <button
                v-if="img.name"
                type="button"
                :disabled="deletingImageName === img.name"
                class="rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-bold text-white shadow-md hover:bg-rose-700 disabled:opacity-60 transition"
                @click="deleteImage(img.name)"
              >
                {{ deletingImageName === img.name ? 'Deleting...' : 'Delete Image' }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="mt-6 py-8 text-center text-sm text-slate-400 italic">
          No images uploaded yet. Upload your first product image above!
        </div>
      </div>

      <!-- Bottom Action -->
      <div class="flex justify-end gap-3 pt-4 border-t border-slate-200">
        <NuxtLink
          :to="`/vendor/${storeSlug}/products`"
          class="rounded-xl bg-teal-700 px-6 py-3 text-sm font-bold text-white shadow-md hover:bg-teal-800 transition"
        >
          Finish &amp; Return to Product Catalog
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
