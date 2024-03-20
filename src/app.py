import asyncio
import logging
import os
from logging import FileHandler, Formatter, StreamHandler, getLogger

from dotenv import find_dotenv, load_dotenv
from fastapi import (
    FastAPI,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


# HTMLをレンダリングするだけの関数
@app.get("/")
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# Websocketを使用して、一つのrouteで送受信ができるようにする
# そうしないと、入力と出力が一緒にできず、他の人が入力した内容で出力してしまう可能性がある
@app.websocket("/chat")
async def chat(ws: WebSocket) -> None:
    # Websocketの接続を確立
    await ws.accept()

    # LLMの初期化
    tripal_gpt = TriPalGPT()

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
        logger.exception(f" {e.__class__.__name__}: {e}")
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
