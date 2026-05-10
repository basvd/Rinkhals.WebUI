import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import tailwindcss from '@tailwindcss/vite';
import svg from '@poppanator/sveltekit-svg';

const __dirname = dirname(fileURLToPath(import.meta.url));
const appJson = JSON.parse(readFileSync(resolve(__dirname, '../rinkhals-webui/app.json'), 'utf-8'));

// Export a Vite config that drops the build artifacts directly in the
// Microdot static directory so the Python dev server can serve them.
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(appJson.version),
  },
  plugins: [tailwindcss(), svelte(), svg()],
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
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
    },
  }
});
