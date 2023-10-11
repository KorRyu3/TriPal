
import os
import openai
from dotenv import load_dotenv


# 環境変数をロード
load_dotenv()

# OpenAI API Keyを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_BASE")
openai.api_type = os.environ.get("OPENAI_API_TYPE")
openai.api_version = os.environ.get("OPENAI_API_VERSION")


