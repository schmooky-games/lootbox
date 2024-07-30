FROM python:3.11

ARG REDIS_URI
ENV REDIS_UR =$REDIS_URI

RUN mkdir /lootbox_service

WORKDIR /lootbox_service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
