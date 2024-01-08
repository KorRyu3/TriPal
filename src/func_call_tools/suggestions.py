import os
import json
from typing import Tuple, Dict, Union, Literal
import random

import requests
from dotenv import load_dotenv, find_dotenv

# from pydantic import BaseModel, Field
# Fieldの使い方は下記を参照
# https://docs.pydantic.dev/latest/concepts/fields/
#
# ↓ LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from langchain_core.pydantic_v1 import BaseModel, Field
# v1Fieldの使い方は下記を参照
# https://docs.pydantic.dev/1.10/usage/schema/


# ---------- 初期化処理 ---------- #
# 環境変数をロード
load_dotenv(find_dotenv())

TRIPADVISOR_API_KEY = os.environ.get("TRIPADVISOR_API_KEY")
HEADERS = {
    "accept": "application/json",
    }
# ------------------------------- #


# Toolで利用する関数の入力スキーマの定義例
class TravelProposalSchema(BaseModel):

    loc_search: str = Field(
        # デフォルト値を設定することができる
        default="",
        # このフィールドのタイトル
        title='LocationSearchQuery',
        # 詳細な説明を記載することができる
        description='Text to use for searching based on the name of the location. Required parameter.',
        # e.g.の記載
        examples= ['日本の有名な観光スポット', '東京都にあるホテル', '北海道の名所', '東京タワー', '旭山動物園', '京都の有名レストラン', '別府温泉杉乃井ホテル'],
    )

    category: Literal["", "hotels", "attractions", "restaurants", "geos"] = Field(
        default="",
        title='Category',
        description='Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos". Arbitrary parameter',
        examples=['', 'hotels', 'attractions', 'restaurants', 'geos'],
    )



# ------Tool(Function Calling)で利用する関数の定義------ #

# 観光スポットの提案
def get_trip_suggestions_info(loc_search: str = "", category: Literal["", "hotels", "attractions", "restaurants", "geos"] = "") -> Union[str, Dict[str, Dict[str, str]]]:
    """
        検索情報(とカテゴリ)を与えて、おすすめの観光スポットを返す

        :param loc_search: Text to use for searching based on the name of the location.
        :param category: Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos".
    """

    language = "ja"
    currency = "JPY"

    # loc_search が入力されていない場合は、"検索したい場所を入力してください"を返す
    # ただ、function callingの特性上ほぼありえない
    if loc_search == "":
        return "検索したい場所を入力してください"

    loc_ids, other_info = get_location_id(loc_search, category, language)

    if not loc_ids:
        return f"情報が取得出来ませんでした。もう一度やり直してください。\n\n{other_info}"

    # 場所の情報を取得
    output = {}

    # APIコールのお金節約のため、ロケーションIDをランダムにinfo_count個選ぶ
    info_count = 5
    ls = range(0, 10)
    rand_ls = list(random.sample(ls, info_count))
    for rand_index in rand_ls:

        loc_id = loc_ids[rand_index]
        min_loc_info = other_info[loc_id]
        loc_info = get_location_info(loc_id, min_loc_info, language, currency)

        # get_location_info()の中でerrorレスポンスが返ってくると"name"すら返ってこないので、min_loc_infoから取ってきてます。その方が確実
        output[min_loc_info["name"]] = loc_info

    return output


# ロケーションの検索をし、ロケーションIDを取得する
def get_location_id(loc_search: str, category: str, language: str) ->  Tuple[list[str], Dict[str, Dict[str, str]]]:
    """
    ロケーションの検索をし、ロケーションIDを取得する

    :param loc_search: search query
    :param category: search category
    :param language: language of the response

    :return loc_ids: list of location ids
    :return loc_info: dict of location information
    """
    # パラメータの設定
    id_param = f"?key={TRIPADVISOR_API_KEY}&language={language}&searchQuery={loc_search}"

    if category:
        id_param += "&category=" + category

    url = f"https://api.content.tripadvisor.com/api/v1/location/search"
    response = requests.get(url + id_param, headers=HEADERS)

    # error handling
    if 500 <= response.status_code <= 599:
        print("response.status_code: ", response.status_code)
        print("response.text: ", response.text)
        return [], {"error": response.text}

    res_dict = json.loads(response.text)

    if "error" in res_dict:
        print("res_dict(error): ", res_dict)
        print("res_dict(error): ", res_dict["error"])
        return [], {"error": res_dict["error"]}
    elif "message" in res_dict:
        print("res_dict(message): ", res_dict)
        print("res_dict(message): ", res_dict["message"])
        return [], {"message": res_dict["message"]}


    loc_ids = []
    other_info = {}
    for res_data in res_dict["data"]:
        # responseの中からロケーションIDを取得
        location_id = res_data["location_id"]
        loc_ids.append(location_id)

        # ロケーションの最低限の情報を取得
        # get_location_info()のレスポンスにたまにエラーが含まれることがあるから、その対策(力技)
        min_loc_info = {}
        min_loc_info["name"] = res_data.get("name", "名前なし")
        min_loc_info["country"] = res_data.get("address_obj", {}).get("country", "国なし")
        min_loc_info["address"] = res_data.get("address_obj", {}).get("address_string", "住所なし")

        other_info[location_id] = min_loc_info

    return loc_ids, other_info


# ロケーションIDに基づいた、ロケーションの情報を取得する
def get_location_info(loc_id: str, min_loc_info: dict, language: str, currency: str) -> Dict[str, str]:
    """
    ロケーションIDに紐づいた、ロケーションの情報を取得する

    :param loc_id: location id
    :param min_loc_info: other information of the location by get_location_id()
    :param language: language of the response
    """
    # パラメータの設定
    loc_param = f"/{loc_id}/details?key={TRIPADVISOR_API_KEY}&language={language}&currency={currency}"
    url = "https://api.content.tripadvisor.com/api/v1/location"
    response = requests.get(url + loc_param, headers=HEADERS)

    # error handling
    if 500 <= response.status_code <= 599:
        return {"error": response.text}

    res_dict = json.loads(response.text)

    # errorの場合は、other_loc_info[name, country, address] をそのまま返す
    # res_status = list(res_dict.keys())[0]
    if "error" in res_dict:
        return min_loc_info

    loc_info_dict = {}
    loc_info_dict["name"] = res_dict.get("name", "名前なし")
    loc_info_dict["description"] = res_dict.get("description", "詳細なし")
    loc_info_dict["web_url"] = res_dict.get("Web_url", "TripadvisorのURL無し")
    loc_info_dict["country"] = res_dict.get("address_obj", {}).get("country", "国なし")
    loc_info_dict["address"] = res_dict.get("address_obj", {}).get("address_string", "住所なし")
    loc_info_dict["email"] = res_dict.get("email", "メールアドレスなし")
    loc_info_dict["phone"] = res_dict.get("phone", "電話番号なし")
    loc_info_dict["website"] = res_dict.get("website", "公式Webサイトなし")
    loc_info_dict["weekly_hours"] = res_dict.get("hours", {}).get("weekday_text", "営業時間情報なし")

    return loc_info_dict
