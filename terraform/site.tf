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
