terraform {
  backend "gcs" {
    bucket = "birdclef-2023-tfstate"
    prefix = "birdclef-2023-public"
  }
}

locals {
  project_id = "birdclef-2023"
  region     = "us-central1"
  repo_name  = local.project_id
  owner      = "dsgt-birdclef"
}

provider "google" {
  project = local.project_id
  region  = local.region
}

data "google_project" "project" {}

resource "google_project_service" "default" {
  for_each = toset([
    "artifactregistry",
    "run",
    "cloudbuild",
    "iam",
    "cloudkms",
    "secretmanager",
    "batch",
  ])
  service = "${each.key}.googleapis.com"
}

resource "google_artifact_registry_repository" "default" {
  location      = local.region
  repository_id = local.repo_name
  format        = "DOCKER"
  depends_on    = [google_project_service.default["artifactregistry"]]
}

// get the compute engine default service account
data "google_compute_default_service_account" "default" {
  project = local.project_id
}

// grant the compute engine default service account push access to the artifact registry
resource "google_artifact_registry_repository_iam_member" "default" {
  repository = google_artifact_registry_repository.default.name
  location   = google_artifact_registry_repository.default.location
  role       = "roles/artifactregistry.repoAdmin"
  member     = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

// grant the compute engine default service account batch agent reporter
resource "google_project_iam_member" "batch-agent-reporter" {
  project = local.project_id
  role    = "roles/batch.agentReporter"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_storage_bucket" "default" {
  name     = local.project_id
  location = "US"
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
  cors {
    origin          = ["*"]
    method          = ["GET"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_binding" "default-public" {
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers"
  ]
}

output "bucket_name" {
  value = google_storage_bucket.default.name
}

// we create a new policy that allows developers to be editor, compute admin, and storage admin
locals {
  // members in the crypto module
  team_info = nonsensitive({
    for entry in yamldecode(data.sops_file.default["team_info_yaml"].raw).members :
    entry.username => entry.email
  })
  members = {
    for username, email in local.team_info :
    username => "user:${email}"
  }
}

resource "google_project_iam_member" "editor" {
  for_each = local.members
  project  = local.project_id
  role     = "roles/editor"
  member   = each.value
}

resource "google_project_iam_member" "compute-admin" {
  for_each = local.members
  project  = local.project_id
  role     = "roles/compute.admin"
  member   = each.value
}

resource "google_project_iam_member" "storage-admin" {
  for_each = local.members
  project  = local.project_id
  role     = "roles/storage.admin"
  member   = each.value
}
