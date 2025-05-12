import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    host: true,     // щоб слухати на 0.0.0.0
    port: 5173,     // твій порт фронта
    proxy: {
      // проксувати всі запити з префіксом /api/ на бек
      '/dev': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
        secure: false,
      },
      '/users': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
        secure: false,
      },
      '/cases': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
      },
      '/wallets': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
      },
      '/balance': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
      },
      '/rates': {
        target: 'http://cryptocases_api:8000',
        changeOrigin: true,
      },
    }
  }
})
