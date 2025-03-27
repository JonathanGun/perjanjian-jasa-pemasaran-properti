import base64
import io
import pdfkit
from fastapi.templating import Jinja2Templates
from src.pdf_generator import PerjanjianJasaPemasaranPropertiPDFGenerator

templates = Jinja2Templates(directory="static/templates")
template = templates.get_template("template_v1.html.j2")


class PDFKitPerjanjianJasaPemasaranPropertiPDFGenerator(
    PerjanjianJasaPemasaranPropertiPDFGenerator
):
    def generate(self, data):
        data = data.model_dump()
        with open("static/images/logo.png", "rb") as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            data["logo_image"] = f"data:image/png;base64,{logo_b64}"

        rendered = template.render(data)
        options = {
            "page-size": "Legal",
            "margin-top": "0mm",  # Minimize margins to maximize content area
            "margin-right": "0mm",
            "margin-bottom": "0mm",
            "margin-left": "0mm",
            "encoding": "UTF-8",
        }

        pdf_stream = io.BytesIO(pdfkit.from_string(rendered, options=options))
        pdf_stream.seek(0)
        return pdf_stream
