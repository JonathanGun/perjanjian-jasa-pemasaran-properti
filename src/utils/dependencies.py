from src.pdfkit_pdf_generator import PDFKitPerjanjianJasaPemasaranPropertiPDFGenerator
from src.pymupdf_pdf_generator import PyMuPDFPerjanjianJasaPemasaranPropertiPDFGenerator
from src.utils.config import config
from src.utils.storage import GoogleDriveClient, LocalStorageClient


def get_pdf_generator():
    if config.USE_HTML_PDF_GENERATOR:
        return PDFKitPerjanjianJasaPemasaranPropertiPDFGenerator()
    return PyMuPDFPerjanjianJasaPemasaranPropertiPDFGenerator()


def get_storage_client():
    if config.HEPI_FF_UPLOAD_TO_DRIVE:
        return GoogleDriveClient()
    return LocalStorageClient()
