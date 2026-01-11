FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (use libpq-dev instead of postgresql-dev for Debian)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    sqlmodel==0.0.16 \
    pydantic==2.6.0 \
    psycopg2-binary==2.9.9 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    bcrypt==4.1.2 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0

# Copy the application code
COPY app/ ./app/

# Expose the port (Hugging Face will set PORT env var)
EXPOSE 7860

# Start the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
