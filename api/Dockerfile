FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --user -r requirements.txt


FROM python:3.13-slim AS runner

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH="/root/.local/bin:$PATH"

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT"]
