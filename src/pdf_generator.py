import abc
import pymupdf
import io
from src.models import DataPerjanjianPemasaranProperti


class PDFGenerator(abc.ABC):
    def __init__(self, config):
        self.config = config

    @abc.abstractmethod
    def generate(self, *args, **kwargs) -> io.BytesIO:
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


class PerjanjianJasaPemasaranPropertiPDFGenerator(PDFGenerator, abc.ABC):
    @abc.abstractmethod
    def generate(self, data: DataPerjanjianPemasaranProperti) -> io.BytesIO:
        pass


class PyMuPDFPerjanjianJasaPemasaranPropertiPDFGenerator(
    PerjanjianJasaPemasaranPropertiPDFGenerator
):
    def __init__(self, config):
        self.config = config
        self.font_size = 10
        self.title_font_size = 14
        self.header_font_size = 12
        self.margin = 50
        self.line_height = 15
        self.current_y = 50

    def generate(self, data: DataPerjanjianPemasaranProperti) -> io.BytesIO:
        doc = pymupdf.open()
        page = doc.new_page()

        self._draw_header(page, "PERJANJIAN JASA PEMASARAN PROPERTI")
        self.current_y += 20

        # Transaction Type
        self._draw_label_value(page, "Jenis Transaksi", data.transaction_type)

        # Property Type
        self._draw_label_value(page, "Jenis Properti", data.property_type)

        # Property Address
        self._draw_multiline_text(
            page, "Lokasi Listing (Alamat Lengkap): " + data.property_address
        )
        self.current_y += 10

        # Owner Information Table
        self._draw_table_header(page, "Pihak Pemilik", "Contact Person")
        self._draw_table_row(page, ["Nama", data.owner_name], ["Nama", data.cp_name])
        self._draw_table_row(
            page, ["Alamat", data.owner_address], ["Alamat", data.cp_address]
        )
        self._draw_table_row(
            page,
            ["NO. KTP", data.owner_ktp_num],
            ["Telp/HP", data.cp_ktp_num],
        )
        self._draw_table_row(
            page,
            ["Telp/HP", data.owner_phone_num],
            ["Email", data.cp_email],
        )
        self._draw_table_row(
            page,
            ["Email", data.owner_email],
            ["Hubungan", "tmp"],
        )
        self.current_y += 10

        # Property Details Table
        self._draw_table_header(page, "Data Properti", "Fasilitas")
        self._draw_table_row(
            page,
            ["Luas Tanah", f"{data.property_land_area} m²"],
            ["Listrik", f"{data.property_wattage} Watt"],
        )
        self._draw_table_row(
            page,
            ["Luas Bangunan", f"{data.property_building_area} m²"],
            ["Air", data.property_water_type],
        )
        self._draw_table_row(
            page,
            ["Kamar Tidur", data.property_bedroom],
            ["AC", data.property_air_cond_count],
        )
        self._draw_table_row(
            page,
            ["Kamar Mandi", data.property_bathroom],
            ["Telepon", data.property_phone_line_count],
        )
        self._draw_table_row(
            page, ["KT Pembantu", data.property_helper_bedroom or "-"], ["", ""]
        )
        self._draw_table_row(
            page, ["KM Pembantu", data.property_helper_bathroom or "-"], ["", ""]
        )
        self._draw_table_row(
            page,
            ["Garasi / Carport", data.property_garage or "-"],
            ["Furnished", data.property_furniture_completion],
        )
        self._draw_table_row(
            page, ["Jumlah Lantai", data.property_floor_count], ["", ""]
        )
        self._draw_table_row(
            page,
            ["Hadap", data.property_facing_to],
            ["Lampiran Dokumen", ""],
        )
        self._draw_table_row(
            page,
            ["Kondisi Bangunan", data.property_condition],
            [
                f"{checkbox(bool(data.property_certificate_url))} Sertifikat",
                f"{checkbox(bool(data.owner_ktp_url))} KTP",
            ],
        )
        self._draw_table_row(
            page,
            ["Status Sertifikat", data.property_certificate_status],
            [
                f"{checkbox(bool(data.property_pbb_url))} PBB",
                f"{checkbox(bool(data.property_imb_url))} IMB",
            ],
        )
        self.current_y += 10

        # Price
        self._draw_label_value(
            page,
            "Harga Jual / Sewa",
            rupiah_format(data.price),
        )
        self.current_y += 20

        # Terms and Conditions
        terms = [
            "Dengan menandatagani perjanjian ini, pihak pemilik menjamin dan menyatakan bahwa",
            "- Adalah pemilik yang sah yang berhak atas kepemilikan properti di atas",
            "- Properti yang dipasarkan tidak dalam sengketa dengan pihak manapun",
            "- Pemilik bertanggung jawab atas seluruh permasalahan sehubungan dengan kepemilikan properti, dan membebaskan pihak Hepi Property dari permasalahan kepemilikan properti tersebut",
            "",
            f"{checkbox(data.agreement_online_marketing)} Pihak marketing dapat mempromosikan properti tersebut melalui media massa baik cetak, elektronik, maupun media online",
            f"{checkbox(data.agreement_offline_marketing)} Pihak marketing dapat memasang tanda (spanduk/papan) dijual atau disewa pada properti tersebut",
            "",
            f"Apabila properti tersebut terjadi melalui marketing Hepi Property, maka pihak pemilik properti berkewajiban membayar success fee kepada kami sebesar {data.success_fee} % dari nilai transaksi properti tersebut (demikian juga berlaku untuk perpanjangan sewa dengan penyewa yang sama)",
            "",
            "Sebagai pemilik, informasi diatas saya berikan sesuai dengan keadaan yang sebenarnya, apabila diketahui ada perbedaan informasi akan menjadi tanggung jawab saya.",
        ]

        for term in terms:
            if term.startswith("-"):
                self._draw_multiline_text(
                    page, term, x=self.margin + 10, char_per_line=100
                )
            else:
                self._draw_multiline_text(page, term, char_per_line=110)
            self.current_y += self.line_height

        # Signatures
        self.current_y += 20
        self._draw_text(
            page, "Pihak Pemilik", x=self.margin, font_size=self.header_font_size
        )
        self._draw_text(
            page,
            "Pihak Marketing",
            x=self.margin + 300,
            font_size=self.header_font_size,
        )
        self._draw_image(page, data.signature_file, x=self.margin, width=200)
        self._draw_text(page, data.owner_name, x=self.margin)
        self.current_y += 30
        self._draw_text(
            page,
            "PT HIDUP ELSE PROPERTI INDONESIA",
            x=self.margin + 150,
            font_size=self.header_font_size,
        )

        # Save the PDF
        pdf_stream = io.BytesIO()
        doc.save(pdf_stream)
        doc.close()
        pdf_stream.seek(0)

        return pdf_stream

    def _draw_header(self, page, text):
        page.insert_text(
            point=(self.margin, self.current_y),
            text=text,
            fontsize=self.title_font_size,
            fontname="helv",
            fontfile=None,
            color=(0, 0, 0),
        )

    def _draw_label_value(self, page, label, value):
        self._draw_text(page, f"{label}: {value}")
        self.current_y += self.line_height

    def _draw_text(self, page, text, x=None, font_size=None, default_empty="-"):
        if x is None:
            x = self.margin
        if font_size is None:
            font_size = self.font_size

        page.insert_text(
            point=(x, self.current_y),
            text=str(text or default_empty),
            fontsize=font_size,
            fontname="helv",
            color=(0, 0, 0),
        )

    def _draw_multiline_text(
        self, page, text, x=None, font_size=None, char_per_line=80, revert_y=False
    ):
        initial_y = self.current_y
        words = str(text).split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > char_per_line:
                self._draw_text(page, line, x=x, font_size=font_size)
                self.current_y += self.line_height
                line = word
            else:
                if line:
                    line += " "
                line += word
        if line:
            self._draw_text(page, line, x=x, font_size=font_size)
        final_y = self.current_y
        if revert_y:
            self.current_y = initial_y
        return final_y

    def _draw_table_header(self, page, left_header, right_header):
        self._draw_text(page, left_header, x=self.margin)
        self._draw_text(page, right_header, x=self.margin + 250)
        self.current_y += self.line_height

    def _draw_table_row(self, page, left_cells, right_cells):
        # Left column
        self._draw_text(page, left_cells[0], x=self.margin)
        left_y = self._draw_multiline_text(
            page, left_cells[1], x=self.margin + 100, char_per_line=30, revert_y=True
        )

        # Right column
        self._draw_text(page, right_cells[0], x=self.margin + 250)
        right_y = self._draw_multiline_text(
            page,
            right_cells[1],
            x=self.margin + 250 + 100,
            char_per_line=30,
            revert_y=True,
        )
        self.current_y = max(left_y, right_y)
        self.current_y += self.line_height

    def _draw_image(self, page, image: bytes, x=None, y=None, width=None, height=None):
        """Draw an image on the PDF page.

        Args:
            page: The PDF page to draw on
            image: Image bytes data
            x: X position (defaults to current margin)
            y: Y position (defaults to current_y)
            width: Desired width of image (maintains aspect ratio if height is None)
            height: Desired height of image
        """
        if x is None:
            x = self.margin
        if y is None:
            y = self.current_y

        # Create a Pixmap from the image bytes
        img = pymupdf.Pixmap(image)

        # Calculate dimensions if only one is specified
        if width is not None and height is None:
            height = width * img.height / img.width
        elif height is not None and width is None:
            width = height * img.width / img.height

        # Insert the image
        rect = pymupdf.Rect(x, y, x + (width or img.width), y + (height or img.height))
        page.insert_image(rect, pixmap=img)

        # Update current_y position
        self.current_y = rect.y1 + 10  # Add small padding


def rupiah_format(value: int):
    return f"Rp {value:,}".replace(",", ".")


def checkbox(is_checked: bool) -> str:
    return "[v]" if is_checked else "[ ]"


class HTMLPerjanjianJasaPemasaranPropertiPDFGenerator(
    PerjanjianJasaPemasaranPropertiPDFGenerator
):
    def generate(self, data: DataPerjanjianPemasaranProperti) -> io.BytesIO:
        pass
