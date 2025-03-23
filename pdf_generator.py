import abc
import pymupdf
import io
from models import DataPerjanjianPemasaranProperti


class PDFGenerator(abc.ABC):
    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def generate(self) -> pymupdf.Document:
        pass


class DummyPDFGenerator(PDFGenerator):
    def generate(self, name) -> io.BytesIO:
        """Generate a PDF with the given name and upload it to Google Drive."""
        # Create a PDF document
        pdf_stream = io.BytesIO()
        doc = pymupdf.open()
        page = doc.new_page()

        # Add text to the PDF
        text = f"Hello, {name}!"
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

        return pdf_stream


class PerjanjianJasaPemasaranPropertiPDFGenerator(PDFGenerator):
    def generate(self, data: DataPerjanjianPemasaranProperti) -> io.BytesIO:
        """Generate a PDF with the given name and upload it to Google Drive."""
        # Create a PDF document
        pdf_stream = io.BytesIO()
        doc = pymupdf.open()
        page = doc.new_page()

        # Add text to the PDF
        text = f"Hello, {data.name}!"
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

        return pdf_stream
