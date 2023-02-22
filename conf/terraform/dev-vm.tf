// define the base vm instance for developers

resource "google_compute_instance" "dev-vm" {
  for_each     = toset(keys(local.team_info))
  name         = "${each.key}-dev"
  machine_type = "n2-standard-4"
  zone         = "${local.region}-a"
  labels = {
    app     = "dev"
    version = "ubuntu-2204"
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 100
    }
    auto_delete = false
  }
  network_interface {
    network = "default"
    access_config {
    }
  }
  scheduling {
    automatic_restart           = false
    instance_termination_action = "STOP"
    on_host_maintenance         = "TERMINATE"
    provisioning_model          = "SPOT"
    preemptible                 = true
  }
  service_account {
    email  = data.google_compute_default_service_account.default.email
    scopes = ["cloud-platform"]
  }
  // ignore changes to current status and cpu_platform
  lifecycle {
    ignore_changes = [
      machine_type,
    ]
  }
}
