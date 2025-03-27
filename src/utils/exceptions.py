# Custom exceptions
class FeatureDisabledError(Exception):
    """Custom exception for disabled features"""

    pass


class FileNotFoundError(Exception):
    """Custom exception for file not found errors"""

    pass


class InvalidSignatureError(Exception):
    """Custom exception for invalid signatures"""

    pass


class PDFGenerationError(Exception):
    """Custom exception for PDF generation failures"""

    pass
