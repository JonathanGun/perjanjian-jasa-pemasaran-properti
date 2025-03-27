FROM python:3.13-slim

WORKDIR /app

# Install system dependencies including wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    xfonts-75dpi \
    xfonts-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY static/ static/
COPY src/ src/

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]