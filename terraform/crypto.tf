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

resource "google_kms_crypto_key_iam_member" "sops" {
  crypto_key_id = google_kms_crypto_key.sops.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

output "sops-key" {
  value = google_kms_crypto_key.sops.id
}
