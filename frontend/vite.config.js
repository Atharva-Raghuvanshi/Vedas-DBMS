import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// dev server proxies /api to the Flask backend, so the frontend code
// can just call fetch('/api/...') with no CORS setup
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
