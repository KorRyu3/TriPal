FROM python:3.11.6-slim-bullseye
USER root

# install japanese locale
RUN apt-get update \
    && apt-get -y install locales gcc g++ build-essential curl apt-transport-https \
    && localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
    # Install Microsoft ODBC driver and tools
    # https://learn.microsoft.com/ja-jp/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=debian18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
    # https://github.com/MicrosoftDocs/sql-docs/issues/6494
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18  unixodbc-dev mssql-tools18 \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    && . ~/.bashrc

# set environment variables
ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8 \
    TZ=JST-9 \
    DOCKER_CONTAINER=true

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "cd ./src && uvicorn app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'" ]
