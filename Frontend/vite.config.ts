import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  optimizeDeps: {
    include: ['lucide-react'],
  },
  server: {
    port:8000,
    proxy: {
      '/api': {
        target: 'http://40.81.255.102:8080',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
