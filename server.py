from fastapi import FastAPI, HTTPException, Response
from config import config
from storage import GoogleDriveClient
from pdf_generator import DummyPDFGenerator, PerjanjianJasaPemasaranPropertiPDFGenerator
from models import DataPerjanjianPemasaranProperti, User
from logger import logger

# Initialize FastAPI app
app = FastAPI()

# Initialize Google Drive client and PDF generator
google_drive_client = GoogleDriveClient(config.HEPI_SERVICE_ACCOUNT_FILE)
# pdf_generator = DummyPDFGenerator(config)
pdf_generator = PerjanjianJasaPemasaranPropertiPDFGenerator(config)


# Endpoint to generate, upload, and share a PDF
@app.post("/submit/")
async def submit(data: DataPerjanjianPemasaranProperti):
    if not config.HEPI_FF_SUBMIT_FORM:
        logger.warning("Submit feature is disabled")
        raise HTTPException(status_code=403, detail="Feature is disabled")

    try:
        # Generate and upload the PDF
        logger.info(f"Generating PDF for user: {data.name}")
        pdf_stream = pdf_generator.generate(data)

        filename = f"hello_{data.name}.pdf"
        logger.info(f"Uploading PDF to Google Drive: {filename}")
        file_id = google_drive_client.upload(
            pdf_stream, filename, config.HEPI_PDF_RESULT_DRIVE_ID
        )

        # Share the file with the user's email
        logger.info(f"Sharing PDF with email: {data.email}")
        google_drive_client.share(file_id, data.email)

        logger.info(f"PDF uploaded and shared successfully: {file_id}")
        return {"message": "PDF uploaded and shared", "file_id": file_id}
    except Exception as e:
        logger.error(f"Error in /submit/ endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    if not config.HEPI_FF_DOWNLOAD_PDF:
        logger.warning("Download PDF feature is disabled")
        raise HTTPException(status_code=403, detail="Feature is disabled")

    try:
        # Get the file URL
        try:
            logger.info(f"Fetching file by name: {filename}")
            file_url = google_drive_client.get_file_url(filename)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")

        # Redirect to the file URL
        logger.info(f"Redirecting to sharable link: {file_url}")
        return Response(
            status_code=302,
            headers={"Location": file_url},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the server
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
