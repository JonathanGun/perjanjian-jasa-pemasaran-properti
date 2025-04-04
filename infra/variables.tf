variable "project" {
  description = "The Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region"
  type        = string
  default     = "us-central1"
}

# cloud run variables
variable "pdf_generator_image" {
  description = "The image for the PDF generator service"
  type        = string
}

variable "pdf_result_drive_id" {
  description = "The Google Drive folder ID for storing PDF results"
  type        = string
}

variable "pdf_generator_feature_flag_download_pdf" {
  description = "Feature flag for downloading PDFs"
  type        = bool
  default     = false
}

variable "pdf_generator_feature_flag_submit_form" {
  description = "Feature flag for accepting form submissions"
  type        = bool
  default     = false
}

variable "pdf_generator_feature_flag_upload_to_drive" {
  description = "Feature flag for uploading to Google Drive"
  type        = bool
  default     = false
}

variable "pdf_generator_feature_flag_save_file_locally" {
  description = "Feature flag for saving files locally"
  type        = bool
  default     = false
}

variable "pdf_generator_port" {
  description = "The port for the PDF generator service"
  type        = number
  default     = 8000
}

variable "pdf_generator_tally_signing_secret" {
  description = "The signing secret for tally"
  type        = string
}
