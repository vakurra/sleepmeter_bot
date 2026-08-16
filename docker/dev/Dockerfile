FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY docker/dev/requirements.txt .
COPY docker/prod/requirements.txt ./prod-requirements.txt

RUN sed -i 's#../prod/requirements.txt#prod-requirements.txt#' requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["watchfiles", "python", "main.py"]