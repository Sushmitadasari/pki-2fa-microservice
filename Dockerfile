# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

# Work inside /app
WORKDIR /app

# Environment tweaks
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies into /install to copy later
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    rm -rf /root/.cache/pip


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

# Basic env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Working directory inside container
WORKDIR /app

# Install system packages: cron + timezone data
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/* && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code and required files
COPY app ./app
COPY scripts ./scripts
COPY cron ./cron
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .
COPY requirements.txt .

# Create volume mount points and set permissions
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Install cron job from file (we'll create cron/2fa-cron in Step 10)
RUN chmod 644 cron/2fa-cron && crontab cron/2fa-cron

# Declare volumes so Docker knows these are external data dirs
VOLUME ["/data", "/cron"]

# Expose API port 8080 (as required)
EXPOSE 8080

# Set environment variable so app uses /data/seed.txt inside container
ENV SEED_FILE_PATH=/data/seed.txt

# Start both cron daemon and API server
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
