import type { LoadEvent } from "@sveltejs/kit";

export async function load({ fetch }: LoadEvent) {
  let resp = await fetch("/api/v1/data/processed/mixit_visualize_subset/subset.json");
  return {
    subset: await resp.json(),
  };
}
