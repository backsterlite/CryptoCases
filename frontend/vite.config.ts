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
    allowedHosts: [
      "d405-93-175-80-8.ngrok-free.app",
      "85c5-93-175-80-8.ngrok-free.app",
      "localhost:8000",
      "d422-93-175-80-8.ngrok-free.app"
    ]
  },
  define: {
    'import.meta.env.PROD': JSON.stringify(process.env.NODE_ENV === 'production')
  },
})
