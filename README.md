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

Copy and put the service account key in a json file, ie: `serviceaccounts/hepi-properti.json`

Copy the service account's email, and give permission to the PDF result's drive folder.
* Go to https://drive.google.com/
* Create folder, share to the service account with editor access
* Copy the Drive Folder ID. The folder ID is the part of the URL after folders/. For example:

    ```txt
    https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J
    ```

    The folder ID is `1A2B3C4D5E6F7G8H9I0J`.


Setup python `venv`

```bash
python3 -m pip venv venv
source venv/bin/activate
```

Install requirements

```bash
pip install -r requirements.txt
```

