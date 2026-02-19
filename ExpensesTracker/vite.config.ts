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
      '/link': 'http://localhost:8000',
      '/item': 'http://localhost:8000',
      '/accounts': 'http://localhost:8000',
      '/identity': 'http://localhost:8000',
      '/transactions': 'http://localhost:8000'
    }
  },
})
