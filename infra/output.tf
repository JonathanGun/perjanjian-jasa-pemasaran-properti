output "service_account_key" {
  value     = google_service_account_key.drive_uploader_key.private_key
  sensitive = true
}

output "cloud_run_url" {
  value = google_cloud_run_v2_service.pdf_generator_service.uri
}
