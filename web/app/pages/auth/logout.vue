<script lang="ts" setup>
const authStore = useAuthStore()

onMounted(async () => {
  await authStore.logout()
  await navigateTo("/auth/login")
})
</script>
<template>
<div></div>
</template>
