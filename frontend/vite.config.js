import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/novel-to-script/',
  plugins: [react()],
  server: {
    port: 5173,
  },
});

