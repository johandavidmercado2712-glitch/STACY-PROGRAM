import { defineConfig } from 'astro/config';

// El sitio se sirve en la raiz / (ver vercel.json: rewrites -> /frontend).
// `base` en '/' hace que Astro genere assets y enlaces relativos a la raiz.
export default defineConfig({
  site: 'https://stacyprogram.online',
  base: '/',
  trailingSlash: 'never',
  build: {
    format: 'directory',
    outDir: './dist',
  },
  vite: {
    build: {
      assetsInlineLimit: 0,
    },
  },
});
