FROM python:3.11

ARG REDIS_URI
ENV REDIS_URI=$REDIS_URI

RUN mkdir /lootbox_service

WORKDIR /lootbox_service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["gunicorn", "src.main:app",  "--bind", "0.0.0.0:8000", "--workers", "4", \
    "--worker-class", "uvicorn.workers.UvicornWorker"]
