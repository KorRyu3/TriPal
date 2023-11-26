import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# DALL-E 3で画像を生成するclass
class DallE3:
    # クラスの初期化処理
    def __init__(self):
        azure_dalle_api_key = os.environ.get("OPENAI_API_DALLE_KEY")
        azure_dalle_api_base = os.environ.get("OPENAI_API_DALLE_BASE")
        azure_dalle_api_version = os.environ.get("OPENAI_API_DALLE_VERSION")
        azure_dalle_api_deployment = os.environ.get("OPENAI_API_DALLE_DEPLOYMENT")

        self.client = AzureOpenAI(
            api_version=azure_dalle_api_version,
            azure_endpoint=azure_dalle_api_base,
            api_key=azure_dalle_api_key,
            azure_deployment=azure_dalle_api_deployment,
        )

    def create_image(self, prompt: str) -> str:
        result = self.client.images.generate(
            model="dall-e-3", # the name of your DALL-E 3 deployment
            # prompt="虹色に輝くデフォルメされたおじいちゃん",
            prompt=prompt,
            n=1,
            quality="standard",
        )

        image_url = json.loads(result.model_dump_json())['data'][0]['url']

        print(image_url)

        return image_url
