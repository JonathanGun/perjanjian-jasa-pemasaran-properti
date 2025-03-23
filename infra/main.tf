provider "google" {
  project = var.project
  region  = var.region
}

resource "google_project_service" "drive_api" {
  service = "drive.googleapis.com"
}

resource "google_service_account" "drive_uploader" {
  account_id   = "drive-uploader" # Name of the service account
  display_name = "Service Account for Google Drive Uploads"
}

resource "google_service_account_key" "drive_uploader_key" {
  service_account_id = google_service_account.drive_uploader.name
}

output "service_account_key" {
  value     = google_service_account_key.drive_uploader_key.private_key
  sensitive = true
}
