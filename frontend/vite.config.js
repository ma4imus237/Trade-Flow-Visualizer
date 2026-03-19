import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          maplibre: ["maplibre-gl", "react-map-gl"],
          deckgl: ["@deck.gl/core", "@deck.gl/layers", "@deck.gl/react"],
          plotly: ["plotly.js-dist-min", "react-plotly.js"],
        },
      },
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
