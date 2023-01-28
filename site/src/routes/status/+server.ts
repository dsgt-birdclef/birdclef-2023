import { json } from "@sveltejs/kit";

export async function GET() {
  return json({
    status: "ok",
    mode: import.meta.env.MODE,
    version: "__VERSION__",
    build_time: "__BUILD_TIME__",
    commit_sha: import.meta.env.COMMIT_SHA || "unknown",
    ref_name: import.meta.env.REF_NAME || "unknown",
    namespace: import.meta.env.NAMESPACE || "development",
  });
}
