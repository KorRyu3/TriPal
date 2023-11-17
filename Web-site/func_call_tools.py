# from pydantic import BaseModel, Field

# Fieldの使い方は下記を参照
# https://docs.pydantic.dev/latest/concepts/fields/


# ↓ LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from pydantic.v1 import BaseModel , Field

# v1Fieldの使い方は下記を参照
# https://docs.pydantic.dev/1.10/usage/schema/

import requests
import os
from dotenv import load_dotenv
import json

# 環境変数をロード
load_dotenv()

# Toolで利用する関数の入力スキーマの定義例
class TravelProposalSchema(BaseModel):

    loc_name: str = Field(
        # デフォルト値を設定することができる
        default=None,
        # このフィールドのタイトル
        title='LocationName',
        # 詳細な説明を記載することができる
        description='Text to use for searching based on the name of the location. Required parameter.',
        # e.g.の記載
        examples= ['日本', 'America', '東京都', '大宮市', '東京タワー', '旭山動物園', 'サイゼリヤ', '別府温泉杉乃井ホテル'],
    )

    category: str = Field(
        default="",
        title='Category',
        description='Filters result set based on property type. Valid options are "hotels", "attractions", "restaurants", and "geos". Arbitrary parameter',
        examples=['hotels', 'attractions', 'restaurants', 'geos'],
    )


# schemaの確認
# print(MyToolInputSchema.schema_json(indent=3))


# Tool(Function Calling)で利用する関数の定義

# 観光スポットの提案
def suggested_sightseeing_spots(**kwargs: dict) -> str:
    key: str = os.environ.get("TRIADO_API_KEY")
    headers = {"accept": "application/json"}

    # ツールの処理
    # 辞書の引数を取り出す
    loc_name = kwargs.get("loc_name")
    category = kwargs.get("category")
    language = "ja"

    print(loc_name, category)


    # 場所のidを取得
    id_param = "?key=" + key

    if loc_name is None:
        return "検索したい場所の名前を入力してください"
    else:
        id_param += "&searchQuery=" + loc_name

    if category != "":
        id_param += "&category=" + category

    id_param += "&language=" + language
    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    print(url + id_param)
    response = requests.get(url + id_param, headers=headers)
    print(response)

    # jsonの中身を取り出す
    # response = json.loads(response)
    res_loc_id = response.text


    # 場所の情報を取得
    loc_id = res_loc_id
    language = "ja"
    currency = "JPY"

    loc_param = f"/{loc_id}/details?key={key}&language={language}&currency={currency}"
    url = "https://api.content.tripadvisor.com/api/v1/location"
    response = requests.get(url + loc_param, headers=headers)
    
    # jsonの中身を取り出す
    output = response.text

    return output
