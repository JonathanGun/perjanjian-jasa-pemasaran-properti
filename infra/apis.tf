resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "iam" {
  service = "iam.googleapis.com"
}

resource "google_project_service" "service_usage" {
  service = "serviceusage.googleapis.com"
}

resource "google_project_service" "drive_api" {
  service = "drive.googleapis.com"
}
