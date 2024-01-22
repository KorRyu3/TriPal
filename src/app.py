import asyncio
import os

# FastAPI
from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

from tripalgpt import TriPalGPT

app = FastAPI()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory="static"), name="static")


# template engineの設定
templates = Jinja2Templates(directory="templates")




# HTMLをレンダリングするだけの関数
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
    )

# Websocketを使用して、一つのrouteで送受信ができるようにする
# そうしないと、入力と出力が一緒にできず、他の人が入力した内容で出力してしまう可能性がある
# sessionがうんちゃらかんちゃらってhiroさんが言ってた。
# sessionって何ですか？？？？？？？？？？？？？？？？？？？？
@app.websocket('/chat')
async def chat(ws: WebSocket):
    # LLMの初期化
    tripal_gpt = TriPalGPT()

    # Websocketの接続を確立
    await ws.accept()

    # Websocketの接続が切れるまで、ユーザーの入力を受け取る
    while True:
        # ユーザーの入力を受け取る
        user_chat = await ws.receive_text()

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


if __name__ == '__main__':
    # Static directoryの読み込みをHTTPSに強制する
    # proxy_headers=Trueにすることで、HTTPをHTTPSに強制する
    # forwarded_allow_ips="*"にすることで、IPアドレスを強制する
    uvicorn.run("app:app", host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
