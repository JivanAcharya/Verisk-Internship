import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
  // Load env variables based on current mode (e.g., development, production)
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [react(), tailwindcss()],
    optimizeDeps: {
      include: ['lucide-react'],
    },
    server: {
      port: 8000,
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_URL,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
