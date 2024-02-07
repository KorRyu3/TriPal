import json
import os
from typing import Literal, Tuple, Union

import requests
from dotenv import find_dotenv, load_dotenv

# ↓ LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from pydantic.v1 import BaseModel, Field

# from pydantic import BaseModel, Field
# Fieldの使い方は下記を参照
# https://docs.pydantic.dev/latest/concepts/fields/

# v1Fieldの使い方は下記を参照
# https://docs.pydantic.dev/1.10/usage/schema/


# ---------- 初期化処理 ---------- #
# 環境変数をロード
load_dotenv(find_dotenv())
HEADERS = {"accept": "application/json"}
BOOKING_API_KEY = os.environ.get("BOOKING_API_KEY")
# ------------------------------- #


# Toolで利用する関数の入力スキーマの定義例
class TravelReservationSchema(BaseModel): ...


# ------Tool(Function Calling)で利用する関数の定義------ #


def reserve_location(**kwargs) -> None: ...


def _get_list_cities(**kwargs) -> None: ...


def _find_matching_props(**kwargs) -> None:
    ...

    list_cities = _get_list_cities(**kwargs)

    ...

    property_id = ...

    ...

    return property_id, ...


def _get_details_props(**kwargs) -> None:
    ...

    (property_id,) = _find_matching_props(**kwargs)

    ...

    return property_id, ...


def _get_property_availability_prices(**kwargs) -> None:
    ...

    property_id, details_props = _get_details_props(**kwargs)

    ...
