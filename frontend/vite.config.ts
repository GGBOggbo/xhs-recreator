import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://hongxin-api:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://hongxin-api:8000',
        ws: true,
      },
    },
  },
})
