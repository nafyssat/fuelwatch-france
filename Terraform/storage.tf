terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
  }
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
}

provider "cloudflare" {}

resource "cloudflare_r2_bucket" "bronze" {
  account_id = var.cloudflare_account_id
  name       = "fuelwatch-france-bronze"
  location   = "WEUR"
}