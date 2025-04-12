import abc
import io
from src.models import DataPerjanjianPemasaranProperti


class PDFGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, *args, **kwargs) -> bytes:
        pass


class PerjanjianJasaPemasaranPropertiPDFGenerator(PDFGenerator, abc.ABC):
    @abc.abstractmethod
    def generate(self, data: DataPerjanjianPemasaranProperti) -> bytes:
        pass
