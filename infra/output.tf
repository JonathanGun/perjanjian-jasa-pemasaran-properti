output "service_account_key" {
  value     = google_service_account_key.drive_uploader_key.private_key
  sensitive = true
}
