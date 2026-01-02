# -------- Dockerfile (psycopg2-binary + Gunicorn) --------
FROM python:3.11-slim

# sane defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn psycopg2-binary

# Copy the application code
COPY . .

# Start Gunicorn; Railway provides $PORT
CMD ["sh", "-c", "exec gunicorn 'run:app' -b 0.0.0.0:${PORT:-8080} --workers ${WEB_CONCURRENCY:-2} --threads ${GTHREADS:-4} --timeout ${TIMEOUT:-120} --access-logfile - --error-logfile -"]
