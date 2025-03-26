import base64
import hmac
import hashlib
from fastapi import Depends, FastAPI, Header, Request, Response
from fastapi.responses import JSONResponse
from utils.logger import logger
from utils.config import config
from utils.storage import GoogleDriveClient, LocalStorageClient
from src.pdf_generator import PerjanjianJasaPemasaranPropertiPDFGenerator
from src.models import DataPerjanjianPemasaranProperti
from functools import wraps

# Initialize FastAPI app
app = FastAPI()

# Initialize Google Drive client and PDF generator
google_drive_client = GoogleDriveClient()
local_storage_client = LocalStorageClient()
pdf_generator = PerjanjianJasaPemasaranPropertiPDFGenerator(config)


# Custom exceptions
class FeatureDisabledError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


# Exception handlers
@app.exception_handler(FeatureDisabledError)
async def feature_disabled_handler(request: Request, exc: FeatureDisabledError):
    logger.warning(f"Feature disabled: {str(exc)}")
    return JSONResponse(
        status_code=403,
        content={"message": "Feature is disabled"},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    logger.warning(f"File not found: {str(exc)}")
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )


@app.exception_handler(InvalidSignatureError)
async def invalid_signature_handler(request: Request, exc: InvalidSignatureError):
    logger.warning(f"Invalid signature: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={"message": "Invalid signature"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


# Decorators
def check_feature_enabled(feature_flag: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not getattr(config, feature_flag, False):
                raise FeatureDisabledError(f"{feature_flag} is disabled")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


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
    logger.debug(f"Received Tally signature: {tally_signature}")
    payload = await request.body()
    if tally_signature is None or not verify_tally_signature(payload, tally_signature):
        raise InvalidSignatureError()
    return True


# Endpoint to generate, upload, and share a PDF
@app.post("/submit/")
@check_feature_enabled("HEPI_FF_SUBMIT_FORM")
async def submit(
    data: DataPerjanjianPemasaranProperti,
    _: bool = Depends(verify_webhook),
):
    logger.debug(f"Received data: {data}")

    # Generate and upload the PDF
    logger.info(f"Generating PDF for user: {data.owner_name}")
    pdf_stream = pdf_generator.generate(data)

    filename = data.get_filename()
    properties = {
        **data.get_form_values(),
        "created_at": data.createdAt,
        "response_id": data.data.responseId,
        "submission_id": data.data.submissionId,
        "respondent_id": data.data.respondentId,
        "filename": filename,
    }
    logger.info(f"PDF generated successfully: {filename}")
    logger.debug(f"PDF properties: {properties}")

    if config.HEPI_FF_UPLOAD_TO_DRIVE:
        logger.info(f"Uploading PDF to Google Drive: {filename}")
        file_id = google_drive_client.upload(
            pdf_stream, filename, config.HEPI_PDF_RESULT_DRIVE_ID, properties
        )

        # Share the file with the user's email
        if data.owner_email:
            logger.info(f"Sharing PDF with email: {data.owner_email}")
            google_drive_client.share(file_id, data.owner_email)

        logger.info(f"PDF uploaded and shared successfully: {file_id}")
        return {"message": "PDF uploaded and shared", "file_id": file_id}

    if config.HEPI_FF_SAVE_FILE_LOCALLY:
        filename = data.data.responseId + ".pdf"
        logger.info(f"Saving PDF locally: {filename}")
        local_storage_client.upload(pdf_stream, filename)
        return {"message": "PDF saved locally", "filename": filename}

    logger.warning("No action taken for the PDF")
    return {"message": "No action taken for the PDF"}


@app.get("/pdf/{response_id}")
@check_feature_enabled("HEPI_FF_DOWNLOAD_PDF")
async def get_pdf(response_id: str):
    logger.info(f"Fetching file by response_id: {response_id}")
    file_url = google_drive_client.get_file_url(response_id)

    # Redirect to the file URL
    logger.info(f"Redirecting to sharable link: {file_url}")
    return Response(
        status_code=302,
        headers={"Location": file_url},
    )


# Run the server
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
