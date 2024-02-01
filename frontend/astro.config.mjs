import { defineConfig } from "astro/config";

import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  outDir: "../backend/static",
  base: "/backend/build/",
  integrations: [tailwind()]
});