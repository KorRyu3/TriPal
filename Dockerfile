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

WORKDIR /app/Web-site

EXPOSE 8000

CMD ["python3", "app.py"]
