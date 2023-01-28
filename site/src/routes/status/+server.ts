import { json } from "@sveltejs/kit";

export async function GET() {
  return json({
    status: "ok",
    mode: import.meta.env.MODE,
    version: "__VERSION__",
    build_time: "__BUILD_TIME__",
    commit_sha: "__COMMIT_SHA__",
    ref_name: "__REF_NAME__",
    namespace: "__NAMESPACE__",
  });
}
