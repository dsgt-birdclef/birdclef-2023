export async function load({ fetch }) {
  const resp = await fetch("/status");
  const client_status = await resp.json();
  return { client_status };
}
