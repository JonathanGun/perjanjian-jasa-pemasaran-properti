import base64
import hmac
import hashlib
from fastapi import Depends, FastAPI, HTTPException, Header, Request, Response
from utils.logger import logger
from utils.config import config
from utils.storage import GoogleDriveClient
from src.pdf_generator import PerjanjianJasaPemasaranPropertiPDFGenerator
from src.models import DataPerjanjianPemasaranProperti

# Initialize FastAPI app
app = FastAPI()

# Initialize Google Drive client and PDF generator
google_drive_client = GoogleDriveClient()
# pdf_generator = DummyPDFGenerator(config)
pdf_generator = PerjanjianJasaPemasaranPropertiPDFGenerator(config)


# Dependency to verify the API key
async def verify_api_key(api_key: str = Header(None, alias="x-api-key")):
    if api_key is None or api_key != config.API_KEY:
        logger.error("Invalid API key")
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


# Function to verify the Tally signature
def verify_tally_signature(payload: bytes, received_signature: str) -> bool:
    """
    Verify the Tally webhook signature.
    """
    digest = hmac.new(
        config.TALLY_SIGNING_SECRET.encode("utf-8"), payload, digestmod=hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, received_signature.encode("utf-8"))


# Dependency to verify the Tally signature
async def verify_webhook(
    request: Request, tally_signature: str = Header(None, alias="tally-signature")
):
    payload = await request.body()
    if tally_signature is None or not verify_tally_signature(payload, tally_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return True


# Endpoint to generate, upload, and share a PDF
@app.post("/submit/")
async def submit(
    data: DataPerjanjianPemasaranProperti,
    _: bool = Depends(verify_webhook),
    __: bool = Depends(verify_api_key),
):
    if not config.HEPI_FF_SUBMIT_FORM:
        logger.warning("Submit feature is disabled")
        raise HTTPException(status_code=403, detail="Feature is disabled")

    logger.debug(f"Received data: {data}")

    try:
        # Generate and upload the PDF
        logger.info(f"Generating PDF for user: {data.name}")
        pdf_stream = pdf_generator.generate(data)

        filename = f"{data.data.responseId}.pdf"
        logger.info(f"Uploading PDF to Google Drive: {filename}")
        file_id = google_drive_client.upload(
            pdf_stream, filename, config.HEPI_PDF_RESULT_DRIVE_ID
        )

        # Share the file with the user's email
        if data.user_email:
            logger.info(f"Sharing PDF with email: {data.user_email}")
            google_drive_client.share(file_id, data.user_email)

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
            filename = f"{filename}.pdf"
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
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
