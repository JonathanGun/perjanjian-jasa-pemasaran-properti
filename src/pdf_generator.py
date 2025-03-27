import abc
import io
from src.models import DataPerjanjianPemasaranProperti


class PDFGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, *args, **kwargs) -> io.BytesIO:
        pass


class PerjanjianJasaPemasaranPropertiPDFGenerator(PDFGenerator, abc.ABC):
    @abc.abstractmethod
    def generate(self, data: DataPerjanjianPemasaranProperti) -> io.BytesIO:
        pass
