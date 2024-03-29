# TriPal
TriPal is an AI service that **proposes travel plans** and provides **reservation proposals** for accommodation facilities in the form of conversations.

[English](./README.md) | [日本語](./README_jp.md)

## Tech Stack
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

## Installation
※ If using Docker as described in [Usage②](#usage-run-with-docker), only [Step0](#step0-clone-this-repository) is necessary.
### Step0: Clone this repository
```bash
$ git clone https://github.com/KorRyu3/TriPal
$ cd TriPal
```

### Step1: Make Virtual Environment
```bash
$ python3 -m venv .venv

# Activate the virtual environment
## Windows
> .\.venv\Scripts\activate
## MacOS or Linux
$ source .venv/bin/activate
```

#### If you want to deactivate the virtual environment
```bash
$ deactivate
```

### Step2: Install Requirements
```bash
$ pip install -r requirements.txt
```

## Usage
There are two ways to run the app: with a local Python environment and with Docker.

## Usage①: Run with Local Python Environment
### Step0: Activate Environment
```bash
# Windows
> .\.venv\Scripts\activate
## MacOS or Linux
$ source .venv/bin/activate
```

### Step1: Run App
```bash
$ python3 src/app.py
```

### Step2: Access to the App
Open your browser and access to `http://127.0.0.1:8000/`.


## Usage②: Run with Docker
### Step0: Build and Run Docker Container
```bash
$ docker-compose up --build
```

### Step1: Access to the App
Open your browser and access to `http://127.0.0.1:8000/`.

## Directory Structure
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

## Developers Information

### About Environment Variables
The environment variables are managed by `.env` file.
The file should be placed in `src/` directory.
Also, the contents of `.env` are as follows:
```bash
# .env

# Azure
# Azure OpenAI API
AZURE_OPENAI_API_DEPLOYMENT="<Deployment name>"
AZURE_OPENAI_API_KEY="<API key>"
AZURE_OPENAI_API_BASE="<Endpoint (base URL)>"
AZURE_OPENAI_API_VERSION="<Azure OpenAI's Version>"

# LangSmith
LANGCHAIN_API_KEY="<LangChain's API key>"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="<Project name>"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# TripAdvisor API
TRIPADVISOR_API_KEY="<Tripadvisor's API key>"

# Rakuten API
RAKUTEN_APPLICATION_ID="<Rakuten Developer's Application ID>"
RAKUTEN_AFFILIATE_ID="<Rakuten Developer's Affiliate ID>"
```

### Contribution Guide
You can see the contribution guide in [CONTRIBUTING.md](./CONTRIBUTING.md).

## Contributors
<!-- generateの仕方は https://contrib.rocks/preview を参照 -->
<a href="https://github.com/KorRyu3/TriPal/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=KorRyu3/TriPal" />
</a>
