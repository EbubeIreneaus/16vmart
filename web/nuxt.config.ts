// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@vueuse/nuxt',
    'nuxt-echarts',
    '@pinia/nuxt'
  ],
  css: ['~/assets/css/main.css'],
  fonts: {
    families: [{ name: 'DM Sans', provider: 'google' }]
  },
  icon: {
    serverBundle: 'local'
  },


  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
    }
  },
  vite: {
    server: {
      allowedHosts: ["localhost", "localhost:3000", "da74-102-91-97-173.ngrok-free.app"]
    }
  }
})