import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  // Tell Vite the project root is the frontend/ subdirectory
  root: 'frontend',

  build: {
    // Output relative to root (frontend/), so dist lands at frontend/dist
    outDir: '../dist',
    emptyOutDir: true,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react':  ['react', 'react-dom', 'react-router-dom'],
          'vendor-charts': ['recharts'],
          'vendor-map':    ['leaflet', 'react-leaflet'],
          'vendor-motion': ['framer-motion'],
          'vendor-ui':     ['lucide-react', 'clsx', 'axios', 'date-fns'],
        },
      },
    },
  },

  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
