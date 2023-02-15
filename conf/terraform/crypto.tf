resource "google_kms_key_ring" "sops" {
  name       = "sops"
  location   = "global"
  depends_on = [google_project_service.default["cloudkms"]]
}

resource "google_kms_crypto_key" "sops" {
  name            = "sops-default"
  key_ring        = google_kms_key_ring.sops.id
  rotation_period = "100000s"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key_iam_binding" "sops" {
  crypto_key_id = google_kms_crypto_key.sops.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = [
    "serviceAccount:${data.google_compute_default_service_account.default.email}"
  ]
}

output "sops-key" {
  value = google_kms_crypto_key.sops.id
}


// list all the secrets and upload them into the secrets manager
locals {
  filenames = {
    for path in fileset(path.module, "../secrets/*") :
    replace(replace(basename(path), ".sops", ""), ".", "_") => path
  }
}

// https://registry.terraform.io/providers/carlpett/sops/latest/docs
provider "sops" {}

data "sops_file" "default" {
  for_each    = local.filenames
  source_file = each.value
  input_type  = endswith(each.value, ".json") ? "json" : "raw"
}

resource "google_secret_manager_secret" "default" {
  for_each  = local.filenames
  secret_id = each.key
  replication {
    automatic = true
  }
  depends_on = [google_project_service.default["secretmanager"]]
}

resource "google_secret_manager_secret_version" "default" {
  for_each    = local.filenames
  secret      = google_secret_manager_secret.default[each.key].id
  secret_data = data.sops_file.default[each.key].raw
}

resource "google_secret_manager_secret_iam_binding" "binding" {
  for_each  = local.filenames
  secret_id = google_secret_manager_secret.default[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${data.google_compute_default_service_account.default.email}",
    "serviceAccount:${google_service_account.cloudbuild.email}",
  ]
}
