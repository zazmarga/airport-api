FROM python:3.11-slim
LABEL maintainer="zazmargo@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . .
RUN mkdir -p /files/media && \
    adduser --disabled-password --no-create-home my_user && \
    chown -R my_user /files/media && \
    chmod -R 755 /files/media

USER my_user
