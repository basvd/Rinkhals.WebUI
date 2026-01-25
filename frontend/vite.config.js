import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

// Export a Vite config that drops the build artifacts directly in the
// Microdot static directory so the Python dev server can serve them.
export default defineConfig({
  plugins: [svelte()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: '../rinkhals-webui/static/dist',
    emptyOutDir: true,
    sourcemap: true
  },
  server: {
    port: 5173,
    strictPort: true
  }
});
