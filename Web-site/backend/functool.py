# from pydantic import BaseModel, Field

# Fieldの使い方は下記を参照
# https://docs.pydantic.dev/latest/concepts/fields/


# ↓ LangChainが利用しているpydanticのバージョンが古いため、v1を利用する
from pydantic.v1 import BaseModel , Field

# v1Fieldの使い方は下記を参照
# https://docs.pydantic.dev/1.10/usage/schema/

import requests


# Toolで利用する関数の入力スキーマの定義例
class MyToolInputSchema(BaseModel):

    text: str = Field(
        # デフォルト値を設定することができる
        default='default',
        # このフィールドのタイトル
        title='Password',
        # 詳細な説明を記載することができる
        description='Password of the user',
        # e.g.の記載
        examples= ['123456'],
    )

    count: int = Field(
        default=1,
        title='Count',
        description='カウントする数',
        examples=['12', '14'],
    )


# schemaの確認
# print(MyToolInputSchema.schema_json(indent=3))


# Toolで利用する関数の定義例
def my_tool_func(**kwargs):

    text = kwargs["text"]
    
    count = kwargs["count"]
    
    # ツールの処理

    output = "output"
    return output




# 空室検索
def search_hotel_vacancy(**kwargs):
    

    res_json = requests.get("URL")
    
    # jsonの中身を取り出す


    return "output"
