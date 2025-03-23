# Perjanjian Jasa Pemasaran Properti

## Development

Prepare gcloud project

```bash
gcloud config configurations create hepi-properti
gcloud config configurations activate hepi-properti
gcloud auth login
gcloud auth application-default login
```

Prepare credentials for terraform
```bash
cp terraform.tfstate.example terraform.tfstate
```

Prepare the resources in GCP (service account and Google Drive API)

```bash
terraform init
terraform plan
terraform apply
terraform output service_account_key
```

Copy and put the service account key in a json file, ie: `~/.sa/hepi-properti.json`
