import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/kit/vite";
import { mdsvex } from "mdsvex";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  extensions: [".svelte", ".svx", ".md"],
  preprocess: [
    vitePreprocess(),
    mdsvex({
      extensions: [".md", ".svx"],
    }),
  ],

  kit: {
    adapter: adapter(),
  },
};

export default config;
