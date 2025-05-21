# Dockerfile - FastAPI backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY lambda/main.py .
RUN pip install fastapi mangum uvicorn boto3

# Expose port
EXPOSE 8001

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
