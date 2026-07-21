<script setup lang="ts">
import type { Page } from '~/types/api'
const props = defineProps<{ page: Page<unknown> }>()
const emit = defineEmits<{ change: [page: number] }>()
</script>
<template>
  <div class="mt-8 flex items-center justify-between border-t border-slate-200 pt-5 text-sm text-slate-500">
    <span>Showing {{ page.items.length }} of {{ page.total }} results</span>
    <div class="flex gap-2"><button class="rounded-lg border border-slate-200 px-3 py-2 disabled:opacity-40" :disabled="page.page === 1" @click="emit('change', props.page.page - 1)">Previous</button><span class="rounded-lg bg-teal-50 px-3 py-2 font-semibold text-teal-800">{{ page.page }} / {{ page.pages }}</span><button class="rounded-lg border border-slate-200 px-3 py-2 disabled:opacity-40" :disabled="page.page === page.pages" @click="emit('change', props.page.page + 1)">Next</button></div>
  </div>
</template>
