import base64
import hmac
import hashlib
import time
from fastapi import Depends, FastAPI, Header, Request, Response
from fastapi.responses import JSONResponse
from src.pdf_generator import PDFGenerator
from src.utils.logger import logger
from src.utils.config import config
from src.utils.dependencies import get_pdf_generator, get_storage_client
from src.utils.storage import GoogleDriveClient, LocalStorageClient, StorageClient
from src.utils.exceptions import (
    FeatureDisabledError,
    FileNotFoundError,
    InvalidSignatureError,
    PDFGenerationError,
)
from src.models import DataPerjanjianPemasaranProperti
from functools import wraps


app = FastAPI()


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


@app.exception_handler(PDFGenerationError)
async def pdf_generation_handler(request: Request, exc: PDFGenerationError):
    logger.error(f"PDF generation failed: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Failed to generate PDF"},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request started, path={request.url.path}, method={request.method}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Request completed, path={request.url.path}, status_code={response.status_code}, process_time={process_time:.2f}s"
    )
    return response


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
    if config.ENVIRONMENT in ["development", "test", "local"]:
        logger.debug("Skipping signature verification in development/test/local")
        return True

    logger.debug(f"Received Tally signature: {tally_signature}")
    payload = await request.body()
    if tally_signature is None or not verify_tally_signature(payload, tally_signature):
        raise InvalidSignatureError()
    return True


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Endpoint to generate, upload, and share a PDF
@app.post(
    "/submit/",
    summary="Generate property marketing agreement PDF",
    response_description="PDF generation result",
    responses={
        200: {"description": "PDF generated successfully"},
        403: {"description": "Feature disabled"},
        500: {"description": "PDF generation failed"},
    },
)
@check_feature_enabled("HEPI_FF_SUBMIT_FORM")
async def submit(
    data: DataPerjanjianPemasaranProperti,
    pdf_generator: PDFGenerator = Depends(get_pdf_generator),
    storage_client: StorageClient = Depends(get_storage_client),
    _: bool = Depends(verify_webhook),
):
    logger.debug(f"Received data: {data}")

    # Check if file already exists
    existing_file = storage_client.get_file_url(data.data.responseId)
    if existing_file:
        logger.info(f"File already exists: {existing_file}")
        return {"message": "File already exists", "file_url": existing_file}
    logger.info(f"File does not exist, proceeding with PDF generation")

    # Generate and upload the PDF
    logger.info(f"Generating PDF for user: {data.owner_name}")
    pdf_stream = pdf_generator.generate(data)

    filename = data.get_filename()
    properties = data.get_form_properties()
    logger.info(f"PDF generated successfully: {filename}")
    logger.debug(f"PDF properties: {properties}")

    # Upload the PDF to Google Drive
    logger.info(f"Uploading PDF: {filename}")
    file_id = upload_file(pdf_stream, filename, storage_client, properties)
    if data.owner_email:
        logger.info(f"Sharing PDF with email: {data.owner_email}")
        storage_client.share(file_id, data.owner_email)

    # Upload the supplementary documents if it exists
    logger.info("Uploading supplementary documents")
    if file := data.property_certificate_file:
        upload_filename = filename.replace(".pdf", "_property_certificate.pdf")
        mimetype = data.property_certificate_mime_type
        if mimetype == "image/jpeg":
            upload_filename = upload_filename.replace(".pdf", ".jpg")
        elif mimetype == "image/png":
            upload_filename = upload_filename.replace(".pdf", ".png")
        upload_file(file, upload_filename, storage_client)

    if file := data.owner_ktp_file:
        upload_filename = filename.replace(".pdf", "_owner_ktp.pdf")
        mimetype = data.owner_ktp_mime_type
        if mimetype == "image/jpeg":
            upload_filename = upload_filename.replace(".pdf", ".jpg")
        elif mimetype == "image/png":
            upload_filename = upload_filename.replace(".pdf", ".png")
        upload_file(file, upload_filename, storage_client)

    if file := data.property_pbb_file:
        upload_filename = filename.replace(".pdf", "_property_pbb.pdf")
        mimetype = data.property_pbb_mime_type
        if mimetype == "image/jpeg":
            upload_filename = upload_filename.replace(".pdf", ".jpg")
        elif mimetype == "image/png":
            upload_filename = upload_filename.replace(".pdf", ".png")
        upload_file(file, filename.replace(".pdf", "_property_pbb.pdf"), storage_client)

    if file := data.property_imb_file:
        upload_filename = filename.replace(".pdf", "_property_imb.pdf")
        mimetype = data.property_imb_mime_type
        if mimetype == "image/jpeg":
            upload_filename = upload_filename.replace(".pdf", ".jpg")
        elif mimetype == "image/png":
            upload_filename = upload_filename.replace(".pdf", ".png")
        upload_file(file, filename.replace(".pdf", "_property_imb.pdf"), storage_client)

    logger.info(f"PDF uploaded and shared successfully: {file_id}")
    return {"message": "PDF uploaded and shared", "file_id": file_id}


def upload_file(
    file: bytes,
    filename: str,
    storage_client: StorageClient = Depends(get_storage_client),
    custom_property: dict = None,
) -> str:
    """
    Upload a document to Storage Client.
    """
    logger.info(f"Uploading document: {filename}")
    file_id = storage_client.upload(file, filename, config.HEPI_PDF_RESULT_DRIVE_ID, custom_property)
    logger.info(f"Document uploaded successfully: {file_id}")
    return file_id


@app.get("/pdf/{response_id}")
@check_feature_enabled("HEPI_FF_DOWNLOAD_PDF")
async def get_pdf(
    response_id: str,
    storage_client: StorageClient = Depends(get_storage_client),
):
    logger.info(f"Fetching file by response_id: {response_id}")
    file_url = storage_client.get_file_url(response_id)

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
