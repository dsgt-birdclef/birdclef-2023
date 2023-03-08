// define the base vm instance for batch workflows

locals {
  // get ansible files, relative to the root of the terraform module
  basepath      = "${path.module}/../ansible"
  ansible_files = fileset(local.basepath, "**/*")
}

// create an ansible bucket
resource "google_storage_bucket" "ansible" {
  name     = "${local.project_id}-batch-ansible"
  location = "US"
}

// copy the files into an ansible bucket
resource "google_storage_bucket_object" "ansible" {
  for_each = local.ansible_files
  name     = each.key
  bucket   = google_storage_bucket.ansible.name
  source   = "${local.basepath}/${each.value}"
}

resource "google_compute_instance_template" "batch-cpu" {
  name         = "batch-cpu-template"
  machine_type = "n2-standard-8"
  labels = {
    app     = "batch-cpu"
    version = "ubuntu-2204"
  }
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -ex
    apt-get update
    apt-get install -y python3-pip
    pip3 install ansible
    mkdir -p /opt/ansible
    gsutil rsync -r gs://${google_storage_bucket.ansible.name}/ /opt/ansible/
    ansible-playbook -i localhost /opt/ansible/batch-vm.yml
  EOT

  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2204-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = 250
    type         = "pd-ssd"
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
}
