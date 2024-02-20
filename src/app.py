import asyncio
import hashlib
import logging
import os
import random
import string
from logging import FileHandler, Formatter, StreamHandler, getLogger
from typing import Annotated

from dotenv import find_dotenv, load_dotenv
from fastapi import (
    Cookie,
    FastAPI,
    Header,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from azure_sql_db import connecte_db, insert_token
from tripalgpt import TriPalGPT

# --------------- 初期化処理 --------------- #
# cwdを./srcに変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# 環境変数をロード
load_dotenv(find_dotenv())
# ---FastAPI--- #
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# template engineの設定
templates = Jinja2Templates(directory="templates")
# ------------- #

# ---Logの出力--- #
logger = getLogger(__name__)
logger.setLevel(logging.ERROR)
# handlerの設定
# StreamHandler
stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
# FileHandler
file_handler = FileHandler(filename="logs/app.log")
file_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
file_handler.setLevel(logging.ERROR)
logger.addHandler(file_handler)
# ----------------------------------------- #


# ランダムな文字列を生成する関数
def random_name(n: int) -> str:
    """
    ランダムな文字列を生成する関数
    :param n: 文字列の長さ
    """
    rand_lst = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
    return "".join(rand_lst)


# ----------------------------- #


# HTMLをレンダリングするだけの関数
@app.get("/")
def index(request: Request) -> HTMLResponse:
    connecte_db()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# Cookieを設定するエンドポイント
@app.get("/set-cookie")
def set_cookie(
    response: Response, session_id: Annotated[str | None, Cookie()] = None
) -> dict[str, str]:
    if session_id is None:
        session_id = random_name(20)
        # response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="None", secure=True)  # max_ageは秒
        response.set_cookie(key="session_id", value=session_id)  # max_ageは秒
        return {"message": "Cookie has been set.", "session_id": session_id}
    else:
        return {"message": "Cookie is already set.", "session_id": session_id}


# Websocketを使用して、一つのrouteで送受信ができるようにする
# そうしないと、入力と出力が一緒にできず、他の人が入力した内容で出力してしまう可能性がある
@app.websocket("/chat")
async def chat(
    ws: WebSocket,
    session_id: Annotated[str | None, Cookie()] = None,
    sec_websocket_key: Annotated[str | None, Header()] = None,
) -> None:
    # Websocketの接続を確立
    await ws.accept()

    # WebSocketのリクエストheaderに含まれるSec-Websocket-Keyと、Cookieのsession_idを利用して、トークンを発行する
    # 取得するCookieやHeader名は、同じ引数名で指定する必要がある
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-WebSocket-Accept
    token = f"{sec_websocket_key}{session_id}"
    hash_token = hashlib.sha1(token.encode("utf-8")).hexdigest()

    token_id = insert_token(hash_token)
    # LLMの初期化
    tripal_gpt = TriPalGPT(token_id)

    try:
        # Websocketの接続が切れるまで、ユーザーの入力を受け取る
        while True:
            # ユーザーの入力を受け取る
            user_chat = await ws.receive_text()

            # チャットボットにユーザーの入力を渡して、応答を取得する
            # responseは非同期generator
            async for output in tripal_gpt.get_async_generator_output(
                user_input=user_chat
            ):
                # 応答を送信する
                # UXのために、0.03秒待つ
                # 0秒だと早すぎて目で追えない
                await asyncio.sleep(0.03)
                # Websocketに応答を送信
                await ws.send_text(output)
                await asyncio.sleep(0)
    except WebSocketDisconnect:
        del tripal_gpt
    except Exception as e:
        # エラーをログに出力
        logger.exception(f" {e.__class__.__name__}: {e}   token: {hash_token}")
        await ws.send_text(
            "エラーが発生しました。 しばらくしてから再度お試しください。"
        )


# demoページ
@app.get("/we-are/demo")
def we_are_demo(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="we-are-demo.html",
    )


# ----------------------------- #
if __name__ == "__main__":
    # 環境変数 `DOCKER_CONTAINER` が設定されていれば、Dockerでの実行とみなす
    if os.environ.get("DOCKER_CONTAINER"):
        # ここでは何もしない
        pass
    else:
        import uvicorn
        # Static directoryの読み込みをHTTPSに強制する
        # proxy_headers=Trueにすることで、HTTPをHTTPSに強制する
        # forwarded_allow_ips="*"にすることで、IPアドレスを強制する
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            proxy_headers=True,
            forwarded_allow_ips="*",
            reload=True,
        )
