<script setup lang="ts">
import type { NuxtError } from '#app'

// Accept the error prop
const props = defineProps<{
  error: NuxtError
}>()

// Clear the error and redirect to the homepage
const handleError = () => {
  clearError({ redirect: '/' })
}
</script>

<template>
  <div class="error-container">
    <!-- Customize based on status code -->
    <template v-if="error.status === 404">
      <h1>404 - Page Not Found</h1>
      <p>Sorry, the page you are looking for doesn't exist or has been moved.</p>
    </template>
    
    <template v-else>
      <h1>{{ error.status}} - {{ error.statusText }} An error occurred</h1>
      <p>{{ error.data?.detail as any ?? "Internal server error"}}</p>
    </template>

    <button @click="handleError">
      Go Back Home
    </button>
  </div>
</template>

<style scoped>
.error-container {
  padding: 4rem;
  text-align: center;
  font-family: sans-serif;
}

button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #00dc82;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
