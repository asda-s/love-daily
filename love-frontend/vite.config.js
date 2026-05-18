import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [uni()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler'
      }
    }
  },
  server: {
    proxy: {
      '/user': { target: 'http://localhost:8000', changeOrigin: true },
      '/memory': { target: 'http://localhost:8000', changeOrigin: true },
      '/life': { target: 'http://localhost:8000', changeOrigin: true },
      '/interact': { target: 'http://localhost:8000', changeOrigin: true },
      '/love': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})
