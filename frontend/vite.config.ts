import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "url";
import { compression } from 'vite-plugin-compression2';

export default defineConfig({
  plugins: [
    react(),
    compression({
      algorithms: ['gzip'],
      exclude: [/\.(br)$ /, /\.(gz)$/],
    }),
    compression({
      algorithms: ['brotli'],
      exclude: [/\.(br)$ /, /\.(gz)$/],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
      },
      mangle: {
        safari10: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': [
            '@radix-ui/react-dialog', 
            '@radix-ui/react-dropdown-menu', 
            '@radix-ui/react-select',
            '@radix-ui/react-toast',
            '@radix-ui/react-tooltip',
            '@radix-ui/react-alert-dialog',
            '@radix-ui/react-checkbox'
          ],
          'icons-vendor': ['lucide-react'],
          'forms-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
          'query-vendor': ['@tanstack/react-query'],
          'utils-vendor': ['wouter', 'tailwind-merge', 'class-variance-authority'],
        }
      }
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'lucide-react',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-select',
      '@radix-ui/react-toast',
      '@radix-ui/react-tooltip',
      '@radix-ui/react-alert-dialog',
      '@radix-ui/react-checkbox',
      'react-hook-form',
      '@hookform/resolvers',
      'zod',
      '@tanstack/react-query',
      'wouter',
      'tailwind-merge',
      'class-variance-authority'
    ],
  },
});
