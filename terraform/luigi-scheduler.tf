// define a e2-micro instance to run luigi
resource "google_compute_instance" "luigi" {
  name         = "luigi"
  machine_type = "e2-micro"
  zone         = "${local.region}-a"
  labels = {
    app = "luigi"
  }
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 10
    }
  }
  network_interface {
    network = "default"
    access_config {

    }
  }
  scheduling {
    automatic_restart  = true
    provisioning_model = "STANDARD"
  }
}

output "luigi-vm" {
  value = {
    id          = google_compute_instance.luigi.id
    external_ip = google_compute_instance.luigi.network_interface.0.access_config.0.nat_ip
  }
}
