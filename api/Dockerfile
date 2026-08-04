FROM python:3.13-slim AS builder
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv "${VIRTUAL_ENV}"

COPY pyproject.toml ./

RUN pip install --upgrade pip && pip install .


FROM python:3.13-slim AS runner

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY --from=builder "${VIRTUAL_ENV}" "${VIRTUAL_ENV}"

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"]
