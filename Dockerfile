FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser . .

# The SQLite database (and anything else instance-scoped) lives here.
RUN mkdir -p /app/instance && chown appuser:appuser /app/instance
VOLUME ["/app/instance"]

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/').read()" || exit 1

# Factory entrypoint. Pass SECRET_KEY and (optionally) DATABASE_URL at runtime.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 \"website:create_app()\""]
