import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  outDir: "../backend/static",
  base: "/backend/build/",
});
