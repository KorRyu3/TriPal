from typing import AsyncGenerator
import json
import asyncio

from pydantic import BaseModel
# FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
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
# LLMの初期化
tripal_gpt = TriPalGPT()


# ユーザーの入力を受け取るためのスキーマ
class UserInput(BaseModel):
    user_chat: str

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
    )

@app.post('/chat')
async def chat(body: UserInput):
    print("body: ", body)
    print("body(type): ", type(body))
    print("body.user_chat: ", body.user_chat)

    # チャットボットにユーザーの入力を渡して、応答を取得する
    # responseは非同期generator
    async def async_generator_output() -> AsyncGenerator[str, None]:
        async for output in tripal_gpt.get_async_generator_output(user_input=body.user_chat):
            print("output: ", output)
            data = f"data: {json.dumps({'message': output})}"
            yield data + "\n\n"
            await asyncio.sleep(0)

    # Responseオブジェクトを作成する
    return StreamingResponse(
            content=async_generator_output(),
            media_type='text/event-stream',
        )


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
