FROM python:3.11.6-slim-bullseye
USER root

# install japanese locale
RUN apt-get update && \
    apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8

# set environment variables
ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8 \
    TZ=JST-9

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "cd ./src && mkdir logs && uvicorn app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'" ]
