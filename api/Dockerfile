FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV UV_NO_CACHE=1
ENV UV_COMPILE_BYTECODE=0

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
RUN find /app/.venv -type f -name "*.pyc" -delete 2>/dev/null || true

FROM python:3.13-slim AS runner

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]