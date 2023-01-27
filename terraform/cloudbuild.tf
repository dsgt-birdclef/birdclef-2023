resource "google_service_account" "cloudbuild" {
  account_id = "cloudbuild-${local.repo_name}"
}

resource "google_project_iam_member" "cloudbuild" {
  for_each = toset([
    "roles/iam.serviceAccountUser",
    "roles/logging.logWriter",
    "roles/run.admin",
    "roles/storage.admin",
    "roles/artifactregistry.repoAdmin",
  ])
  project = data.google_project.project.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

resource "google_cloudbuild_trigger" "default" {
  for_each = {
    deploy-site = {
      _VITE_STATIC_HOST = "https://storage.googleapis.com/${google_storage_bucket.default.name}"
    },
    build-birdnet = {},
    build-mixit   = {},
  }
  name = each.key
  github {
    name  = local.repo_name
    owner = local.owner
    push {
      branch       = "^main$"
      invert_regex = false
    }
  }
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  filename           = "cloudbuild/${each.key}.yaml"
  substitutions      = merge(each.value, { _REGION = local.region })
  service_account    = google_service_account.cloudbuild.id
  depends_on = [
    google_project_service.default["cloudbuild"],
    google_project_iam_member.cloudbuild["roles/iam.serviceAccountUser"],
    google_project_iam_member.cloudbuild["roles/logging.logWriter"],
  ]
}
