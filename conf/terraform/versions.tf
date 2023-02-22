terraform {
  required_providers {
    google = {
      source  = "hashicorp/google-beta"
      version = "4.53.1"
    }
    sops = {
      source  = "carlpett/sops"
      version = "0.7.2"
    }
  }
  required_version = ">= 1.0"
}
