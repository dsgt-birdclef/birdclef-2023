resource "google_cloud_run_v2_service" "default" {
  for_each = toset(["live", "next"])
  name     = local.repo_name
  location = local.region

  template {
    scaling {
      max_instance_count = 20
    }
    containers {
      image = "${local.region}-docker.pkg.dev/${local.project_id}/${local.repo_name}/site:${each.key}"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.default["run"]]
}

resource "google_cloud_run_service_iam_member" "all-users" {
  for_each = toset(keys(google_cloud_run_v2_service.default))
  service  = google_cloud_run_v2_service.default[each.key].name
  location = google_cloud_run_v2_service.default[each.key].location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value = {
    for key in keys(google_cloud_run_v2_service.default) :
    key => google_cloud_run_v2_service.default[key].uri
  }
}
