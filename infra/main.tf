resource "google_service_account" "drive_uploader" {
  account_id   = "drive-uploader" # Name of the service account
  display_name = "Service Account for Google Drive Uploads"
}

resource "google_service_account_key" "drive_uploader_key" {
  service_account_id = google_service_account.drive_uploader.name
}

resource "google_cloud_run_service" "pdf_generator_service" {
  name     = "pdf-generator-service"
  location = var.region

  template {
    spec {
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
      }
      service_account_name = google_service_account.drive_uploader.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
