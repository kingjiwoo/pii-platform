
FROM python:3.11-slim

WORKDIR /app

# Install deps first for layer caching (rebuild only if requirements change)
COPY src/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/api/ ./src/api/

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
