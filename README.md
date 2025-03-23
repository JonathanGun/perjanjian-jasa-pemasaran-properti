# Perjanjian Jasa Pemasaran Properti

## Prerequisites

1. Python
2. Python packages: `pip` and `venv`
3. [ngrok](https://ngrok.com/)

## Tech Stacks

1. [FastAPI](https://fastapi.tiangolo.com/) for the http framework
2. [Pydantic](https://docs.pydantic.dev/latest/) for the data model and validation
3. [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) for generating PDF
4. [Google Cloud Platform](https://console.cloud.google.com/) for the deployment
5. [Google Drive](https://drive.google.com/) for the storage solution
6. [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) for containerization and local build
7. [Google Cloud Run](https://cloud.google.com/run) for production deployment

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

Prepare `.env` and fill the values

```bash
cp .env.example .env
```

Start server

```bash
python server.py
```

Expose to ngrok

```bash
ngrok http 8000
```

Setup [tally](https://tally.so/), connect the webhook

## Deployment

Build the docker image

```bash
make build
```

Push the image to container registry

```bash
make push
```

Deploy to cloud run using terraform

```bash
make deploy
```

Get the cloud run URL and put it in tally webhook and redirection url. Add `/submit` and `/pdf` suffix after the URL.
