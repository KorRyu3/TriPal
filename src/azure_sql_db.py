# https://learn.microsoft.com/ja-jp/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=macos
import os
from datetime import datetime

import pyodbc
from dotenv import find_dotenv, load_dotenv
from pyodbc import DatabaseError

# 環境変数をロード
load_dotenv(find_dotenv())

# データベース接続情報
SERVER = os.environ.get("AZURE_SQL_SERVER")
DATABASE = os.environ.get("AZURE_SQL_DATABASE")
USERNAME = os.environ.get("AZURE_SQL_USERNAME")
PASSWORD = os.environ.get("AZURE_SQL_PASSWORD")
DRIVER = "{ODBC Driver 18 for SQL Server}"
TIMEOUT = 60


DB_CONNECTION_STRING = f"Driver={DRIVER};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout={TIMEOUT};"


def connecte_db() -> None:
    """Azure SQL Databaseに接続する。"""
    # 接続するだけ
    corn = pyodbc.connect(DB_CONNECTION_STRING)
    corn.close()


def insert_token(token: str) -> int:
    """
    tokenをINSERTし、INSERT時に生成されたtoken_idを取得する。

    :param token: INSERTするtoken
    """
    # SCOPE_IDENTITYで、直前に挿入されたIDを取得
    insert_tokens_sql = (
        "INSERT INTO tokens (token) VALUES (?); SELECT SCOPE_IDENTITY();"
    )

    # データベースへの接続
    with pyodbc.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            # tokensテーブルへの挿入
            cursor.execute(insert_tokens_sql, token)
            # 次の結果セットに移動
            cursor.nextset()
            row = cursor.fetchone()
            if row:
                token_id = row[0]
                token_id = int(token_id)
            else:
                token_id = None

            # token_idが正しく取得できているか確認
            if token_id is None:
                raise DatabaseError("Error: Failed to retrieve token_id after insert.")

            # 正常に挿入された場合はコミット
            conn.commit()  # token挿入をコミット

    return token_id


def insert_conversation_history(
    token_id: int, input_text: str, output_text: str, conversation_timestamp: datetime
) -> None:
    """
    Azure SQL Databaseに会話の入出力をINSERTする。

    :param token_id: トークンが挿入された時に生成されるID
    :param input_text: ユーザーからの入力
    :param output_text: AIから生成された出力
    :param conversation_timestamp: 会話のタイムスタンプ。現在の日時を使用
    """

    with pyodbc.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            # INSERT文
            insert_conversation_sql = """
                INSERT INTO conversation_history (token_id, input_text, output_text, conversation_timestamp)
                VALUES (?, ?, ?, ?);
            """
            # クエリの実行
            cursor.execute(
                insert_conversation_sql,
                token_id,
                input_text,
                output_text,
                conversation_timestamp,
            )
            cursor.commit()


# if __name__ == "__main__":
#     import random
#     import pytz
#     from datetime import datetime

#    # 東京タイムゾーンを取得
#    tokyo_timezone = pytz.timezone("Asia/Tokyo")

#    # 現在の日時を東京タイムゾーンで取得
#    current_timestamp = datetime.now(tokyo_timezone)

#     # 接続する
#     connecte_db()

#     # トークンをINSERTする
#     token_id = insert_token(random.randint(100, 10000) * random.randint(100, 10000))
#     # 会話の入出力をINSERTする
#     insert_conversation_history(
#         token_id=token_id,
#         input_text="test_input",
#         output_text="test_output",
#         conversation_timestamp=current_timestamp,
#     )

#     print("Success")
