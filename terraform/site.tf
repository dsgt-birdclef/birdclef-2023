
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

resource "google_cloudbuild_trigger" "github" {
  github {
    name  = local.repo_name
    owner = local.owner
    push {
      branch       = "^main$"
      invert_regex = false
    }
  }
  include_build_logs = "INCLUDE_BUILD_LOGS_WITH_STATUS"
  substitutions = {
    _REGION = local.region
  }
  filename        = "cloudbuild.yaml"
  service_account = google_service_account.cloudbuild.id
  depends_on = [
    google_project_service.default["cloudbuild"],
    google_project_iam_member.cloudbuild["roles/iam.serviceAccountUser"],
    google_project_iam_member.cloudbuild["roles/logging.logWriter"],
  ]
}

resource "google_cloud_run_v2_service" "default" {
  name     = local.repo_name
  location = local.region

  template {
    scaling {
      max_instance_count = 20
    }
    containers {
      image = "${local.region}-docker.pkg.dev/${local.project_id}/${local.repo_name}/site:latest"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.default["run"]]
}

resource "google_cloud_run_service_iam_member" "all-users" {
  service  = google_cloud_run_v2_service.default.name
  location = google_cloud_run_v2_service.default.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value = google_cloud_run_v2_service.default.uri
}
