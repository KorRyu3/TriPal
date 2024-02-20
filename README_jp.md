# TriPal
**旅行プランを提案**し、**宿泊施設などの予約提案**を会話形式で提供するAIサービス。

[English](./README.md) | [日本語](./README_jp.md)

## 使用技術
<!-- シールド一覧 -->
<!-- https://shields.io/badges -->
<!-- https://simpleicons.org/ -->
<p style="display: inline">
    <!-- フロントエンド -->
    <img src="https://img.shields.io/badge/-HTML5-E34F26.svg?logo=html5&logoColor=white&style=for-the-badge">
    <img src="https://img.shields.io/badge/-CSS3-1572B6.svg?logo=css3&logoColor=white&style=for-the-badge">
    <img src="https://img.shields.io/badge/-JavaScript-F7DF1E.svg?logo=javascript&logoColor=black&style=for-the-badge">
    <img src="https://img.shields.io/badge/-Jinja2-B41717.svg?logo=jinja&logoColor=white&style=for-the-badge">
    <!-- バックエンド -->
    <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
    <img src="https://img.shields.io/badge/-FastAPI-009688.svg?logo=fastapi&logoColor=0d0d0d&style=for-the-badge">
    <img src="https://img.shields.io/badge/-LangChain-000000.svg?logo=langchain&logoColor=white&style=for-the-badge">
    <!-- インフラ -->
    <img src="https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=for-the-badge">
    <img src="https://img.shields.io/badge/-github_actions-F9F9F9.svg?logo=github-actions&style=for-the-badge">
    <img src="https://img.shields.io/badge/-azure-0078D4.svg?logo=Microsoft-Azure&style=for-the-badge">
</p>

## インストール
### Step0: リポジトリのクローン
```bash
$ git clone https://github.com/KorRyu3/TriPal
$ cd TriPal
```

### Step1: 仮想環境の作成
```bash
$ python3 -m venv .venv

# 仮想環境を有効化
## Windows
> .\.venv\Scripts\activate
## MacOS or Linux
$ source .venv/bin/activate
```

#### 仮想環境を無効化する場合
```bash
$ deactivate
```

### Step2: 必要なライブラリのインストール
```bash
$ pip install -r requirements.txt
```

### Step3: Microsoft ODBC Driver for SQL Serverのインストール
※ [Usage](#usage②-dockerで実行)でDockerを使用する場合は不要です。
```bash
# macOS
https://learn.microsoft.com/ja-jp/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16

# Homebrewがない場合
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
# Microsoft ODBC Driver for SQL Serverのインストール
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18


# Windows
# CPUアーキテクチャに合わせてインストーラを選択してください
https://learn.microsoft.com/ja-jp/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16


# Linux
# Linuxディストリビューションに合わせてインストーラを選択してください
https://learn.microsoft.com/ja-jp/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
```

## Usage
アプリの起動方法は、ローカルのPython環境で実行する方法と、Dockerで実行する方法の2つがあります。
## Usage①: ローカルのPython環境で実行
### Step0: 仮想環境の有効化
```bash
# Windows
> .\.venv\Scripts\activate
## MacOS or Linux
$ source .venv/bin/activate
```

### Step1: アプリの起動
```bash
$ python3 src/app.py
```

### Step2: アプリへのアクセス
`http://127.0.0.1:8000/`にアクセスすると、アプリが起動します。

## Usage②: Dockerで実行
### Step0: Dockerコンテナのビルドと実行
```bash
$ docker-compose up --build
```

### Step1: アプリへのアクセス
`http://127.0.0.1:8000/`にアクセスすると、アプリが起動します。

## ディレクトリ構成
```bash
TriPal
├── .dockerignore
├── .gitignore
├── CONTRIBUTING.md
├── docker-compose.yml
├── Dockerfile
├── README.md
├── README_jp.md
├── requirements.txt
├── .github
│   └── ...
├── .venv
│   └── ...
├── drawio
│   ├── architecture.drawio
│   ├── first_design.drawio
│   ├── log_ER.drawio
│   └── work-flow.drawio
└── src
    ├── __init__.py
    ├── .env
    ├── app.py
    ├── azure_sql_db.py
    ├── dalle3.py
    ├── llm_prompts.py
    ├── log_setup.py
    ├── tripalgpt.py
    ├── func_call_tools
    │   ├── reservations.py
    │   └── suggestions.py
    ├── logs
    │   ├── .gitingore
    │   └── ...
    ├── static
    │   ├── font
    │   │   └── ...
    │   ├── index.js
    │   └── style.css
    └── templates
        ├── index.html
        └── we-are-demo.html
```

## 開発者向け情報

### 環境変数ファイルについて
環境変数は、`.env`で管理しています。  
envファイルは`src/`に配置してください。  
また、`.env`の中身は以下のようになっています。
```bash
# .env

# Azure
# Azure SQL Database
AZURE_SQL_SERVER="<Server name>"
AZURE_SQL_DATABASE="<Database name>"
AZURE_SQL_USERNAME="<Username>"
AZURE_SQL_PASSWORD="<Password>"

# Azure OpenAI API
AZURE_OPENAI_API_DEPLOYMENT="<Deployment name>"
AZURE_OPENAI_API_KEY="<API key>"
AZURE_OPENAI_API_BASE="<Endpoint (base URL)>"
AZURE_OPENAI_API_VERSION="<Azure OpenAI's Version>"


# TripAdvisor API
TRIPADVISOR_API_KEY="<Tripadvisor's API key>"

# Rakuten API
RAKUTEN_APPLICATION_ID="<Rakuten Developer's Application ID>"
RAKUTEN_AFFILIATE_ID="<Rakuten Developer's Affiliate ID>"
```

### コントリビューター向けのガイドライン
ガイドラインは[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。

## Contributors
<!-- generateの仕方は https://contrib.rocks/preview を参照 -->
<a href="https://github.com/KorRyu3/TriPal/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=KorRyu3/TriPal" />
</a>
