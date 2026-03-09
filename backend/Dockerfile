FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv --break-system-packages && uv sync --frozen --no-dev

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=builder /app/.venv /app/.venv
COPY backend/ ./backend/
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8003
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/api/v1/health')"
CMD ["uvicorn", "backend.src.saas_starter.main:app", "--host", "0.0.0.0", "--port", "8003"]
