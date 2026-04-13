import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "127.0.0.1",
    port: 3000,
    proxy:{
      '/api/ask': { target: 'http://localhost:8001', changeOrigin: true},
      '/api/pipeline': { target: 'http://localhost:8001', changeOrigin: true },
      '/api/upload': { target: 'http://localhost:8001', changeOrigin: true },
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    }
  },
})
