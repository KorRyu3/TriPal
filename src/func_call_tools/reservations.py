import json
import os
from logging import FileHandler, Formatter, getLogger
from typing import Any, Literal

import numpy as np
import requests
from dotenv import find_dotenv, load_dotenv
from opencensus.ext.azure.log_exporter import AzureLogHandler

# ↓ LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from pydantic.v1 import BaseModel, Field

# from pydantic import BaseModel, Field
# Fieldの使い方は下記を参照
# https://docs.pydantic.dev/latest/concepts/fields/

# v1Fieldの使い方は下記を参照
# https://docs.pydantic.dev/1.10/usage/schema/


# ---------- 初期化処理 ---------- #
# directoryをfunc_call_toolsに変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Logの出力
logger = getLogger(__name__)
logger.setLevel("ERROR")
# handlerの設定
file_handler = FileHandler(filename="../logs/reservations.log")
file_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s\n" + "%(message)s"))
file_handler.setLevel("ERROR")
logger.addHandler(file_handler)
# Azure App InsightsにLogを送信するための設定
logger.addHandler(AzureLogHandler())

# 環境変数をロード
load_dotenv(find_dotenv())
HEADERS = {"accept": "application/json"}
RAKUTEN_APPLICATION_ID = os.environ.get("RAKUTEN_APPLICATION_ID")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID")
# 都道府県コード
PREFECTURE_CODE = Literal[
    "",
    "hokkaido",
    "aomori",
    "iwate",
    "miyagi",
    "akita",
    "yamagata",
    "hukushima",
    "ibaragi",
    "tochigi",
    "gunma",
    "saitama",
    "tiba",
    "tokyo",
    "kanagawa",
    "niigata",
    "toyama",
    "ishikawa",
    "hukui",
    "yamanasi",
    "nagano",
    "gihu",
    "shizuoka",
    "aichi",
    "mie",
    "shiga",
    "kyoto",
    "osaka",
    "hyogo",
    "nara",
    "wakayama",
    "tottori",
    "simane",
    "okayama",
    "hiroshima",
    "yamaguchi",
    "tokushima",
    "kagawa",
    "ehime",
    "kouchi",
    "hukuoka",
    "saga",
    "nagasaki",
    "kumamoto",
    "ooita",
    "miyazaki",
    "kagoshima",
    "okinawa",
]
# ------------------------------- #


# Toolで利用する関数の入力スキーマの定義例
class TravelReservationSchema(BaseModel):
    keyword: str = Field(
        default="",
        title="Keyword Hotel Search",
        # 宿泊施設の名前を検索するためのキーワード。 複数のキーワードを指定する場合は半角スペースを区切りとして指定してください。
        description="Text used to search for accommodations. If multiple keywords are specified by separating them with a half-width space, an AND search is performed. Required parameter.",
        examples=[
            "北海道 旅館",
            "東京",
            "那覇 ホテル",
            "名古屋 温泉",
            "函館 旅館 おすすめ",
        ],
    )

    pref_code: PREFECTURE_CODE = Field(
        default="",
        title="Prefecture Code",
        # 都道府県を示すコード。コードは都道府県のローマ字。 このフィールドが指定された場合、指定された地区に属する施設のみが検索対象となります。
        description="A code indicating the prefecture. The code is the Romanized version of the prefecture name. If this field is specified, only facilities belonging to the designated district will be included in the search. Required parameter.",
        examples=["tokyo", "shiga", "hokkaido"],
    )


# ------Tool(Function Calling)で利用する関数の定義------ #


def get_reserve_location(keyword: str, pref_code: str = "") -> dict[str, Any]:
    """
    宿泊施設の情報を取得

    :param keyword: search keyword. space separated. multiple can be specified
    :param pref_code: prefecture code. romaji
    """

    res_dict: dict = _find_matching_props(keyword, pref_code)

    if res_dict.get("error"):
        return res_dict

    # 取得した情報の数を調べる
    length = len(res_dict["hotels"])
    # 情報の数を10個以下に制限
    count = length if length < 10 else 10

    rnd_choices = np.random.choice(length, count, replace=False)

    hotel_info = {}
    for rnd_index in rnd_choices:
        hotel_info_temp = {}

        hotel_name: str = res_dict["hotels"][rnd_index][0]["hotelBasicInfo"][
            "hotelName"
        ]
        hotel_info_temp["hotel_info"] = res_dict["hotels"][rnd_index][0][
            "hotelBasicInfo"
        ]
        hotel_info[hotel_name] = hotel_info_temp

    return hotel_info


def _find_matching_props(
    keyword: str, pref_code: PREFECTURE_CODE = ""
) -> dict[str, Any] | dict[str, str]:
    """
    ロケーション検索の結果を取得する

    :param keyword: search keyword. space separated. multiple can be specified
    :param pref_code: prefecture code. romaji
    """

    # ホテル名、特徴、郵便番号、住所1、住所2、電話番号、ホテル情報URL、宿泊プラン一覧ページ、最低料金、アクセス方法
    elements = "hotelName,hotelSpecial,postalCode,address1,address2,telephoneNo,hotelInformationUrl,planListUrl,hotelMinCharge,access"

    required_param = f"?applicationId={RAKUTEN_APPLICATION_ID}&affiliateId={RAKUTEN_AFFILIATE_ID}&format=json&formatVersion=2"
    optional_param = f"&responseType=small&elements={elements}&keyword={keyword}&middleClassCode={pref_code}"

    url = "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426"

    res = requests.get(url + required_param + optional_param, headers=HEADERS)

    if 500 <= res.status_code <= 599:
        logger.exception(
            f"[Rakuten Server Error(Keyword Hotel Search)] \n"
            f"status_code: {res.status_code}\n"
            f"error text: {res.text}"
        )
        return {"error": "Server Error"}

    dict_data: dict = json.loads(res.text)

    if "error" in dict_data:
        logger.exception(
            f"[Rakuten Error(Keyword Hotel Search)]\n"
            f"error: {dict_data['error']}\n"
            f"error_description: {dict_data['error_description']}"
        )
        return {"error": "Server Error. Please try another keyword."}

    return dict_data
