import { defineConfig } from 'astro/config';

// El sitio se sirve bajo /frontend (ver vercel.json: builds -> src "frontend").
// `base` hace que Astro prefije todos los assets y enlaces internos con /frontend.
export default defineConfig({
  site: 'https://www.stacyprogram.online',
  base: '/frontend',
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
