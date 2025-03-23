FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY utils/ utils/
COPY src/ src/

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]
