<script setup lang="ts">
const props = defineProps({
  message: String,
});
</script>

<template>
  <span class="mt-1 block text-xs font-medium text-rose-600">{{
    props.message
  }}</span>
</template>
