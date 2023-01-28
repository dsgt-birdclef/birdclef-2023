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
    deploy-site-next = {
      filename_prefix = "deploy-site"
      branch          = "^main$"
      substitutions   = { _NAMESPACE = next }
    }
    deploy-site = {
      tag           = "^site-"
      substitutions = { _NAMESPACE = live }
    },
    build-birdnet = { tag = "^app-" },
    build-mixit   = { tag = "^app-" },
  }
  name = each.key
  github {
    name  = local.repo_name
    owner = local.owner
    push {
      branch       = lookup(each.value, "branch", null)
      tag          = lookup(each.value, "tag", null)
      invert_regex = false
    }
  }
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  filename           = "cloudbuild/${lookup(each.value, "filename_prefix", each.key)}.yaml"
  substitutions = merge(
    lookup(each.value, "substitutions", {}),
    {
      _VITE_STATIC_HOST = "https://storage.googleapis.com/${google_storage_bucket.default.name}",
      _REGION           = local.region
  })
  service_account = google_service_account.cloudbuild.id
  depends_on = [
    google_project_service.default["cloudbuild"],
    google_project_iam_member.cloudbuild["roles/iam.serviceAccountUser"],
    google_project_iam_member.cloudbuild["roles/logging.logWriter"],
  ]
}
