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
    proxy: {
      // Усе, що починається з /api → localhost:8000
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,   // підміняє Origin → http://localhost:8000
        secure: false,        // https → http допустимо
        ws: false,            // true, якщо колись будуть WebSocket’и
        // optional: прибираємо префікс, якщо бек НЕ має /api
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
    host: true,     // щоб слухати на 0.0.0.0
    port: 5173,     // твій порт фронта
    allowedHosts: [
      "localhost:8000",
      "3cf7-93-175-80-8.ngrok-free.app",
    ]
  },
})
