from flask import Flask, render_template, request, jsonify
from tripalgpt import TriPalGPT

app = Flask(__name__)

@app.route('/')
def index():
    global tripal_gpt
    tripal_gpt = TriPalGPT()
    return render_template('index.html')


@app.post('/chat')
def chat():
    # FormDataの中身を取り出す
    user_chat = request.form.get('user_chat')

    # チャットボットにユーザーの入力を渡して、応答を取得する
    res = tripal_gpt.get_response(user_input=user_chat)
    # 応答をJSON形式に変換する
    res_json = jsonify({'response': res})

    return res_json


if __name__ == '__main__':
    app.run(debug=True)
