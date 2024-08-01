# Стадия сборки
FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install uv

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8000

CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", \
    "--worker-class", "uvicorn.workers.UvicornWorker", "--threads", "1"]
