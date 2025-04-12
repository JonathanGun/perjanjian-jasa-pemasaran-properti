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
        template_data = data.model_dump()
        owner_signature = data.owner_signature_file
        if owner_signature:
            owner_signature = base64.b64encode(owner_signature).decode("utf-8")
            template_data["owner_signature"] = (
                f"data:image/png;base64,{owner_signature}"
            )
        agent_signature = data.agent_signature_file
        if agent_signature:
            agent_signature = base64.b64encode(agent_signature).decode("utf-8")
            template_data["agent_signature"] = (
                f"data:image/png;base64,{agent_signature}"
            )
        with open("static/images/logo.png", "rb") as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            template_data["logo_image"] = f"data:image/png;base64,{logo_b64}"

        rendered = template.render(template_data)
        options = {
            "page-size": "Legal",
            "margin-top": "0mm",  # Minimize margins to maximize content area
            "margin-right": "0mm",
            "margin-bottom": "0mm",
            "margin-left": "0mm",
            "encoding": "UTF-8",
        }

        return pdfkit.from_string(rendered, options=options)
