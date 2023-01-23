import type { LoadEvent } from "@sveltejs/kit";

export async function load({ fetch }: LoadEvent) {
  let resp = await fetch(
    [
      "/api/v1/data/processed/birdclef-2022",
      "birdnet-embeddings-with-neighbors-agreement-static/v1",
      "agreement.json",
    ].join("/")
  );
  return {
    agreement: await resp.json(),
  };
}
