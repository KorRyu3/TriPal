import json
import logging
import os
import random
from logging import FileHandler, Formatter, StreamHandler, getLogger
from typing import Literal, Tuple

import requests
from dotenv import find_dotenv, load_dotenv

# LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from langchain_core.pydantic_v1 import BaseModel, Field

from log_setup import common_logger

# ---------- 初期化処理 ---------- #
# 現在のdirectoryを取得し、directoryをsrcに変更
cwd = os.getcwd()
cwd = cwd if cwd.endswith("src") else os.path.join(cwd, "src")
# 環境変数をロード
load_dotenv(find_dotenv())
# Logの出力
logger = getLogger(__name__)
logger.setLevel(logging.ERROR)
# handlerの設定
# StreamHandler
stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
# FileHandler
file_handler = FileHandler(filename=f"{cwd}/logs/suggestions.log")
file_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s\n" + "%(message)s"))
file_handler.setLevel(logging.ERROR)
logger.addHandler(file_handler)

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
        title="LocationSearchQuery",
        # 詳細な説明を記載することができる
        description="Text to use for searching based on the name of the location. Required parameter.",
        # e.g.の記載
        examples=[
            "日本の有名な観光スポット",
            "東京都にあるホテル",
            "北海道の名所",
            "東京タワー",
            "旭山動物園",
            "京都の有名レストラン",
            "別府温泉杉乃井ホテル",
        ],
    )

    category: Literal["", "hotels", "attractions", "restaurants", "geos"] = Field(
        default="",
        title="Category",
        description='Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos". Arbitrary parameter',
        examples=["", "hotels", "attractions", "restaurants", "geos"],
    )


# ------Tool(Function Calling)で利用する関数の定義------ #


# 観光スポットの提案
def get_trip_suggestions_info(
    loc_search: str = "",
    category: Literal["", "hotels", "attractions", "restaurants", "geos"] = "",
) -> str | dict[str, dict[str, str]]:
    """
    検索情報(とカテゴリ)を与えて、おすすめの観光スポットを返す

    :param loc_search: Text to use for searching based on the name of the location.
    :param category: Filters result set based on property type. Valid options are "", "hotels", "attractions", "restaurants", and "geos".
    """
    common_logger.info(f"loc_search: {loc_search}, category: {category}")

    language = "ja"
    currency = "JPY"

    # loc_search が入力されていない場合は、"検索したい場所を入力してください"を返す
    # ただ、function callingの特性上ほぼありえない
    if loc_search == "":
        return "検索したい場所を入力してください"

    loc_ids, other_info = _get_location_id(loc_search, category, language)

    common_logger.info(f"loc_ids: {loc_ids}, other_info: {other_info}")

    if loc_ids == []:
        return (
            f"情報が取得出来ませんでした。もう一度やり直してください。\n\n{other_info}"
        )

    # 場所の情報を取得
    output = {}

    # APIコールのお金節約のため、ロケーションIDをランダムにinfo_count個選ぶ
    # We are始まるから制限一時撤廃！
    # info_count = 5
    # ls = range(0, 10)
    # rand_ls = list(random.sample(ls, info_count))
    # for rand_index in rand_ls:
    random.shuffle(loc_ids)  # ロケーションIDをランダムに
    for loc_id in loc_ids:
        # loc_id = loc_ids[rand_index]
        min_loc_info = other_info[loc_id]
        loc_info = _get_location_info(loc_id, min_loc_info, language, currency)

        # get_location_info()の中でerrorレスポンスが返ってくると"name"すら返ってこないので、min_loc_infoから取ってきてます。その方が確実
        output[min_loc_info["name"]] = loc_info

    return output


# ロケーションの検索をし、ロケーションIDを取得する
def _get_location_id(
    loc_search: str, category: str, language: str
) -> Tuple[list[str], dict[str, dict[str, str]]]:
    """
    ロケーションの検索をし、ロケーションIDを取得する

    :param loc_search: search query
    :param category: search category
    :param language: language of the response

    :return loc_ids: list of location ids
    :return loc_info: dict of location information
    """
    # パラメータの設定
    id_param = (
        f"?key={TRIPADVISOR_API_KEY}&language={language}&searchQuery={loc_search}"
    )

    if category != "":
        id_param += "&category=" + category

    url = "https://api.content.tripadvisor.com/api/v1/location/search"
    response = requests.get(url + id_param, headers=HEADERS)

    # error handling
    if 500 <= response.status_code <= 599:
        logger.exception(
            f"[Tripadvisor Server Error(Location Search)] \n"
            f"search query: {loc_search}\n"
            f"url: {url + id_param}\n"
            f"status_code: {response.status_code}\n"
            f"error text: {response.text}"
        )
        return [], {"error": "Server Error"}

    res_dict: dict = json.loads(response.text)

    if "error" in res_dict or "message" in res_dict:
        logger.exception(
            f"[Tripadvisor Error] \n"
            f"search query: {loc_search}\n"
            f"url: {url + id_param}\n"
            f"error text: {res_dict}"
        )
        return [], {"error": "Search Error"}

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
        min_loc_info["country"] = res_data.get("address_obj", {}).get(
            "country", "国なし"
        )
        min_loc_info["address"] = res_data.get("address_obj", {}).get(
            "address_string", "住所なし"
        )

        other_info[location_id] = min_loc_info

    return loc_ids, other_info


# ロケーションIDに基づいた、ロケーションの情報を取得する
def _get_location_info(
    loc_id: str, min_loc_info: dict, language: str, currency: str
) -> dict[str, str]:
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
        logger.exception(
            f"[Tripadvisor Server Error(Location {loc_id} Details)] \n"
            f"url: {url + loc_param}\n"
            f"status_code: {response.status_code}\n"
            f"error text: {response.text}"
        )
        return {"error": "Server Error"}

    res_dict: dict = json.loads(response.text)

    # errorの場合は、other_loc_info[name, country, address] をそのまま返す
    # res_status = list(res_dict.keys())[0]
    if "error" in res_dict:
        return min_loc_info

    loc_info_dict = {}
    loc_info_dict["name"] = res_dict.get("name", "名前なし")
    loc_info_dict["description"] = res_dict.get("description", "詳細なし")
    loc_info_dict["web_url"] = res_dict.get("Web_url", "TripadvisorのURL無し")
    loc_info_dict["country"] = res_dict.get("address_obj", {}).get("country", "国なし")
    loc_info_dict["address"] = res_dict.get("address_obj", {}).get(
        "address_string", "住所なし"
    )
    loc_info_dict["email"] = res_dict.get("email", "メールアドレスなし")
    loc_info_dict["phone"] = res_dict.get("phone", "電話番号なし")
    loc_info_dict["website"] = res_dict.get("website", "公式Webサイトなし")
    loc_info_dict["weekly_hours"] = res_dict.get("hours", {}).get(
        "weekday_text", "営業時間情報なし"
    )

    return loc_info_dict
