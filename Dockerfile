FROM python:3.12-slim

ARG APP_HOME=/evaluation-service

ENV APP_HOME=$APP_HOME

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=$APP_HOME

WORKDIR $APP_HOME

# Copy requirements first for cache-friendly builds
COPY requirements.txt .

# Install build deps, install Python deps, then remove build deps in the same RUN
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create app user / group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy application files
COPY app/ $APP_HOME/app/
COPY configs/ $APP_HOME/configs/

# Fix ownership (use APP_HOME, not /app)
RUN chown -R appuser:appgroup $APP_HOME

# Switch to non-root user
USER appuser

EXPOSE 8000

# Healthcheck using Python stdlib (no extra deps required)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').getcode()==200 else 1)"

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]