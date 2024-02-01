import asyncio
import random, string
from logging import getLogger, StreamHandler, Formatter, FileHandler
from typing import Annotated, Union
import hashlib

# FastAPI
from fastapi import FastAPI, Request, Header, Cookie, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from tripalgpt import TriPalGPT

app = FastAPI()
# app.pyを起動する際は、実行するdirectoryを/src/に変更してから実行しないとここでエラーが出る。
# 原因は本当に不明
# おそらく、こいつが参照するdirectoryが、appから見たものではなく、作業directoryから見たものだと推測できる
app.mount("/static", StaticFiles(directory="static"), name="static")

# template engineの設定
templates = Jinja2Templates(directory="templates")

# ---Logの出力---
logger = getLogger(__name__)
# handlerの設定
handler = StreamHandler()
file_handler = FileHandler(filename="logs/app.log")
# handlerのフォーマットを設定
handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s - %(name)s  %(message)s"))
file_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
# logのレベルを設定
logger.setLevel("INFO")
handler.setLevel("INFO")
file_handler.setLevel("INFO")
# handlerをロガーに追加
logger.addHandler(file_handler)
logger.addHandler(handler)




def random_name(n):
    rand_lst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(rand_lst)



# HTMLをレンダリングするだけの関数
@app.get('/')
def index(request: Request):
    session_id = random_name(20)
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        headers={
            "Set-Cookie": f"session_id={session_id}"
        }
    )

# Websocketを使用して、一つのrouteで送受信ができるようにする
# そうしないと、入力と出力が一緒にできず、他の人が入力した内容で出力してしまう可能性がある
@app.websocket('/chat')
async def chat(ws: WebSocket, session_id: Annotated[str | None, Cookie()] = None, sec_websocket_key: Union[str, None] = Header(default=None)):
    # Websocketの接続を確立
    await ws.accept()

    # WebSocketのリクエストheaderに含まれるSec-Websocket-Keyと、Cookieのsession_idを利用して、トークンを発行する
    # 取得するCookieやHeader名は、同じ引数名で指定する必要がある
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-WebSocket-Accept
    token = sec_websocket_key + session_id
    hash_token = hashlib.sha1(token.encode("utf-8")).hexdigest()
    logger.info(f"WebSocket connected.    token: {hash_token}")
    print(f"Session-ID: {session_id}")

    # LLMの初期化
    tripal_gpt = TriPalGPT(hash_token)

    try:
        # Websocketの接続が切れるまで、ユーザーの入力を受け取る
        while True:
            # ユーザーの入力を受け取る
            user_chat = await ws.receive_text()

            print(f"Session-ID: {session_id}")

            # チャットボットにユーザーの入力を渡して、応答を取得する
            # responseは非同期generator
            async for output in tripal_gpt.get_async_generator_output(user_input=user_chat):
                # 応答を送信する
                # UXのために、0.03秒待つ
                # 0秒だと早すぎて目で追えない
                await asyncio.sleep(0.03)
                # Websocketに応答を送信
                await ws.send_text(output)
                await asyncio.sleep(0)
    except WebSocketDisconnect:
        # Websocket接続が切れたら、ログを出力する
        logger.info(f"WebSocket disconnected. token: {hash_token}")
    except Exception as e:
        # エラーをログに出力
        logger.error(f" {e.__class__.__name__}   token: {hash_token}")
        await ws.send_text("エラーが発生しました。 しばらくしてから再度お試しください。")

if __name__ == '__main__':
    # Static directoryの読み込みをHTTPSに強制する
    # proxy_headers=Trueにすることで、HTTPをHTTPSに強制する
    # forwarded_allow_ips="*"にすることで、IPアドレスを強制する
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*", reload=True)
