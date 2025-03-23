import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    def __init__(self):
        # Google Drive configuration
        self.HEPI_PDF_RESULT_DRIVE_ID = os.getenv("HEPI_PDF_RESULT_DRIVE_ID")

        # Feature flag
        self.HEPI_FF_DOWNLOAD_PDF = (
            os.getenv("HEPI_FF_DOWNLOAD_PDF", "False").lower() == "true"
        )
        self.HEPI_FF_SUBMIT_FORM = (
            os.getenv("HEPI_FF_SUBMIT_FORM", "False").lower() == "true"
        )

        # Other
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.PORT = int(os.getenv("PORT", 8000))


# Singleton instance of Config
config = Config()
