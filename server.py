from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pymupdf
import io

# Initialize FastAPI app
app = FastAPI()


# Pydantic model for the user
class User(BaseModel):
    name: str


# Endpoint to generate and return a PDF
@app.post("/generate-pdf/")
async def generate_pdf(user: User):
    try:
        # Create a PDF document
        pdf_stream = io.BytesIO()
        doc = pymupdf.open()
        page = doc.new_page()

        # Add text to the PDF
        text = f"Hello, {user.name}!"
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

        # Return the PDF as a streaming response
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=hello_{user.name}.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
