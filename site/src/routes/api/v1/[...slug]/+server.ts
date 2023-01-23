import type { RequestEvent } from "./$types";

function build_path(path: string, client: boolean = false): string {
  let base_url = import.meta.env.VITE_STATIC_HOST;
  // if we request the content from the client directly, we need to account
  // for the nginx name from outside the docker netweork
  if (client) {
    base_url = base_url.replace("nginx", "localhost");
  }
  return `${base_url.replace(/\/$/, "")}/${path}`;
}

export async function GET({ url, params, fetch }: RequestEvent) {
  let client = url.searchParams.get("client") === "true";
  let redirect_url = build_path(params.slug, client);
  if (client) {
    return Response.redirect(redirect_url, 302);
  } else {
    return await fetch(redirect_url);
  }
}
