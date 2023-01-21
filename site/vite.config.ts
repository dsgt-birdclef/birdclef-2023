import { sveltekit } from "@sveltejs/kit/vite";
import type { UserConfig } from "vite";
import replace from "@rollup/plugin-replace";

let replaceVersion = () =>
  replace({
    __VERSION__: process.env.npm_package_version,
    __BUILD_TIME__: new Date().toISOString(),
    preventAssignment: true,
  });

const config: UserConfig = {
  plugins: [sveltekit(), replaceVersion()],
};

export default config;
