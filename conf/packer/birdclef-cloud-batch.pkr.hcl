packer {
  required_plugins {
    googlecompute = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/googlecompute"
    }
  }
}

source "googlecompute" "birdclef-cloud-batch" {
  project_id          = "birdclef-2023"
  image_name              = "birdclef-cloud-batch-{{timestamp}}"
  image_family        = "birdclef-cloud-batch"
  source_image_family = "ubuntu-2204-lts"
  ssh_username        = "packer"
  zone                = "us-central1-a"
  disk_size           = "50"
  machine_type        = "n1-standard-2"
  scopes              = ["https://www.googleapis.com/auth/cloud-platform"]
  preemptible         = true
}

build {
  sources = ["sources.googlecompute.birdclef-cloud-batch"]
  // install ansible
  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y python3-pip --no-install-recommends",
      "sudo pip3 install ansible",
    ]
  }
  provisioner "ansible-local" {
    playbook_file = "../ansible/batch.yml"
    playbook_dir  = "../ansible"
  }
}
