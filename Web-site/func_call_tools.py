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
from typing import Tuple, Union
import random


# ---初期化処理---
# 環境変数をロード
load_dotenv()

TRIPADVISOR_API_KEY = os.environ.get("TRIPADVISOR_API_KEY")
HEADERS = {"accept": "application/json"}
# ---------------

# Toolで利用する関数の入力スキーマの定義例
class TravelProposalSchema(BaseModel):

    # ここを辞書型一つにすれば出力は安定する？ 

    loc_search: str = Field(
        # デフォルト値を設定することができる
        default=None,
        # このフィールドのタイトル
        title='LocationSearchQuery',
        # 詳細な説明を記載することができる
        description='Text to use for searching based on the name of the location. Required parameter.',
        # e.g.の記載
        examples= ['日本の有名な観光スポット', '東京都にあるホテル', '北海道の名所', '東京タワー', '旭山動物園', '京都の有名レストラン', '別府温泉杉乃井ホテル'],
    )

    # category: str = Field(
    #     default="",
    #     title='Category',
    #     description='Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos". Arbitrary parameter',
    #     examples=['', 'hotels', 'attractions', 'restaurants', 'geos'],
    # )

    # search_json: dict = Field(
    #     default={"loc_search": None, "category": ""},
    #     title='LocationSearchQuery',
    #     description="""
    #     loc_search: Text to use for searching based on the name of the location. 
    #     category: Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos". 
    #     Input should be a single string strictly in the following JSON format: {"loc_search": "loc_search", "category": "category"}
    #     """,
    #     examples= [
    #         {"loc_search": "東京", "category": ""},
    #         {"loc_search": "日本の有名な観光スポット", "category": "attractions"},
    #         {"loc_search": "東京都にあるホテル", "category": "hotels"},
    #         {"loc_search": "北海道の名所", "category": "attractions"},
    #         {"loc_search": "東京タワー", "category": "attractions"},
    #         {"loc_search": "旭山動物園", "category": "attractions"},
    #         {"loc_search": "京都の有名レストラン", "category": "restaurants"},
    #         {"loc_search": "別府温泉杉乃井ホテル", "category": "hotels"}
    #     ],
    # )


# schemaの確認
# print(MyToolInputSchema.schema_json(indent=3))


# Tool(Function Calling)で利用する関数の定義

# 観光スポットの提案
def suggested_sightseeing_spots(loc_search: str = None, category: str = "") -> Union[str, dict]:
    """
        :param loc_search: Text to use for searching based on the name of the location. 
        :param category: Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos". 
    """

    # 辞書の引数を取り出す
    # search_dict = json.loads(loc_search)
    # loc_search = search_dict.get("loc_search", None)
    # category = search_dict.get("category", "")
    language = "ja"
    currency = "JPY"

    # loc_search が入力されていない場合は、"検索したい場所を入力してください"を返す
    if loc_search is None:
        return "検索したい場所を入力してください"

    # ロケーションIDと、最低限の情報を取得
    loc_ids, other_info = get_location_id(loc_search, category, language)

    # 場所の情報を取得
    output = {}

    # APIコール短縮のため、ロケーションIDをランダムにinfo_count個選ぶ
    info_count = 5
    ls = range(0, 10)
    rand_ls = list(random.sample(ls, info_count))
    for rand_index in rand_ls:

        loc_id = loc_ids[rand_index]
        other_loc_info = other_info[loc_id]
        loc_info = get_location_info(loc_id, other_loc_info, language, currency)

        output[other_loc_info["name"]] = loc_info

    return output


# ロケーションの検索をし、ロケーションIDを取得する
def get_location_id(loc_search: str, category: str, language: str) ->  Tuple[list, dict]:
    """
    ロケーションの検索をし、ロケーションIDを取得する

    :param loc_search: search query
    :param category: search category
    :param language: language of the response

    :return loc_ids: list of location ids
    :return loc_info: dict of location information
    """
    # パラメータの設定
    id_param = "?key=" + TRIPADVISOR_API_KEY
    id_param += "&language=" + language

    id_param += "&searchQuery=" + loc_search

    if category != "":
        id_param += "&category=" + category

    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    response = requests.get(url + id_param, headers=HEADERS)

    # jsonの中身を取り出す
    res_dict = json.loads(response.text)

    loc_ids = []
    other_info = {}
    for res_data in res_dict["data"]:

        # ロケーションIDを取得
        location_id = res_data["location_id"] 
        loc_ids.append(location_id)

        # ロケーションの最低限の情報を取得
        other_loc_info = {}

        other_loc_info["name"] = res_data["name"]
        other_loc_info["country"] = res_data["address_obj"]["country"]
        other_loc_info["address"] = res_data["address_obj"]["address_string"]

        other_info[location_id] = other_loc_info

    return loc_ids, other_info


# ロケーションIDに基づいた、ロケーションの情報を取得する
def get_location_info(loc_id: str, other_loc_info: dict, language: str, currency: str) -> dict:
    """
    ロケーションIDに紐づいた、ロケーションの情報を取得する

    :param loc_id: location id
    :param other_info: other information of the location by get_location_id()
    :param language: language of the response
    """
    # パラメータの設定
    loc_param = f"/{loc_id}/details?key={TRIPADVISOR_API_KEY}&language={language}&currency={currency}"
    url = "https://api.content.tripadvisor.com/api/v1/location"
    response = requests.get(url + loc_param, headers=HEADERS)

    # jsonの中身を取り出す
    res_dict = json.loads(response.text)

    # errorの場合は、other_loc_info[name, country, address] をそのまま返す
    res_status = list(res_dict.keys())[0]
    if res_status == "error":
        return other_loc_info

    # ロケーションの情報を辞書に格納する
    loc_info_dict = {}

    loc_info_dict["name"] = res_dict["name"]
    loc_info_dict["description"] = res_dict.get("description", "詳細なし")
    loc_info_dict["web_url"] = res_dict.get("Web_url", "TripadvisorのURL無し")
    loc_info_dict["country"] = res_dict["address_obj"]["country"]
    loc_info_dict["address"] = res_dict["address_obj"]["address_string"]
    loc_info_dict["email"] = res_dict.get("email", "メールアドレスなし")
    loc_info_dict["phone"] = res_dict.get("phone", "電話番号なし")
    loc_info_dict["website"] = res_dict.get("website", "公式Webサイトなし")
    loc_info_dict["weekly_hours"] = res_dict.get("hours", {}).get("weekday_text", "営業時間情報なし")

    return loc_info_dict
