from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymupdf
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()


# Pydantic model for the user
class User(BaseModel):
    name: str


# Google Drive API setup
SERVICE_ACCOUNT_FILE = os.getenv("HEPI_SERVICE_ACCOUNT_FILE")
PDF_RESULT_DRIVE_ID = os.getenv("HEPI_PDF_RESULT_DRIVE_ID")

if not SERVICE_ACCOUNT_FILE:
    raise ValueError("HEPI_SERVICE_ACCOUNT_FILE environment variable is not set")
if not PDF_RESULT_DRIVE_ID:
    raise ValueError("HEPI_PDF_RESULT_FOLDER_ID environment variable is not set")

SCOPES = ["https://www.googleapis.com/auth/drive"]


def authenticate_google_drive():
    """Authenticate using a service account and return the Google Drive API service."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_to_google_drive(service, file_stream, filename, folder_id=None):
    """Upload a file to Google Drive."""
    file_metadata = {"name": filename}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    media = MediaIoBaseUpload(file_stream, mimetype="application/pdf")
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return file.get("id")


# Endpoint to generate and upload a PDF
@app.post("/generate-pdf/")
async def generate_pdf(user: User):
    try:
        # Create a PDF document
        pdf_stream = io.BytesIO()
        doc = pymupdf.open()
        page = doc.new_page()

        # Add text to the PDF
        text = f"Hello, {user.name}!"
        page.insert_text(
            point=(50, 70),  # Position (x, y) on the page
            text=text,
            fontsize=24,
            fontname="helv",
            color=(0, 0, 0),  # Black color
        )

        # Save the PDF to the stream
        doc.save(pdf_stream)
        doc.close()

        # Reset the stream position to the beginning
        pdf_stream.seek(0)

        # Authenticate Google Drive using the service account
        drive_service = authenticate_google_drive()

        # Upload the PDF to Google Drive
        folder_id = PDF_RESULT_DRIVE_ID
        filename = f"hello_{user.name}.pdf"
        file_id = upload_to_google_drive(drive_service, pdf_stream, filename, folder_id)

        return {"message": "PDF uploaded to Google Drive", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
