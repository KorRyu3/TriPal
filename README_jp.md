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


## Usage
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


## ディレクトリ構成
```bash
TriPal
├── GitRule_README.md
├── README.md
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .venv
│   └── ...
├── drawio
│   ├── architecture.drawio
│   ├── first_design.drawio
│   └── work-flow.drawio
└── src
    ├── .env
    ├── __init__.py
    ├── app.py
    ├── dalle3.py
    ├── llm_prompts.py
    ├── tripalgpt.py
    ├── func_call_tools
    │   ├── reservations.py
    │   └── suggestions.py
    ├── templates
    │   └── index.html
    └── static
        ├── style.css
        └── index.js
```

## 開発者向け情報

### 環境変数ファイルについて
環境変数は、`.env`で管理しています。  
envファイルは`src/`に配置してください。  
また、`.env`の中身は以下のようになっています。
```bash
# .env
# Azure OpenAI API
AZURE_OPENAI_API_DEPLOYMENT="Azure OpenAIのデプロイメント名"
AZURE_OPENAI_API_KEY="Azure OpenAIのAPIキー"
AZURE_OPENAI_API_BASE="Azure OpenAIのエンドポイント (base URL)"
AZURE_OPENAI_API_VERSION="Azure OpenAIのバージョン指定"

# TripAdvisor API
TRIPADVISOR_API_KEY="TripadvisorのAPI key"

# Rakuten API
RAKUTEN_APPLICATION_ID="楽天デベロッパーのアプリケーションID"
RAKUTEN_APPLICATION_SECRET="楽天デベロッパーのアプリケーションシークレット"
RAKUTEN_AFFILIATE_ID="楽天デベロッパーのアフィリエイトID"
```

### Gitのルール
Gitのルールは[GitRule_README.md](./GitRule_README.md)を参照してください。

## Contributors
<!-- generateの仕方は https://contrib.rocks/preview を参照 -->
<a href="https://github.com/KorRyu3/TriPal/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=KorRyu3/TriPal" />
</a>
