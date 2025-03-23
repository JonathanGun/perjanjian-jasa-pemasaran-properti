resource "google_service_account" "drive_uploader" {
  account_id   = "drive-uploader" # Name of the service account
  display_name = "Service Account for Google Drive Uploads"
}

resource "google_service_account_key" "drive_uploader_key" {
  service_account_id = google_service_account.drive_uploader.name
}

resource "google_cloud_run_v2_service" "pdf_generator_service" {
  name     = "pdf-generator-service"
  location = var.region

  template {

    containers {
      image = var.pdf_generator_image
      ports {
        container_port = var.pdf_generator_port
      }
      env {
        name  = "HEPI_PDF_RESULT_DRIVE_ID"
        value = var.pdf_result_drive_id
      }
      env {
        name  = "DEBUG"
        value = "true"
      }
      env {
        name  = "HEPI_FF_DOWNLOAD_PDF"
        value = var.pdf_generator_feature_flag_download_pdf
      }
      env {
        name  = "HEPI_FF_SUBMIT_FORM"
        value = var.pdf_generator_feature_flag_submit_form
      }
      env {
        name  = "HEPI_API_KEY"
        value = var.pdf_generator_api_key
      }
    }
    service_account = google_service_account.drive_uploader.email
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location = google_cloud_run_v2_service.pdf_generator_service.location
  project  = google_cloud_run_v2_service.pdf_generator_service.project
  service  = google_cloud_run_v2_service.pdf_generator_service.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
