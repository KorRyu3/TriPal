from flask import Flask, render_template, request, make_response, Response
from tripalgpt import TriPalGPT

app = Flask(__name__)

@app.route('/')
def index() -> str:
    global tripal_gpt
    tripal_gpt = TriPalGPT()
    return render_template('index.html')


@app.post('/chat')
def chat() -> Response:
    # FormDataの中身を取り出す
    user_chat = request.form.get('user_chat')

    # チャットボットにユーザーの入力を渡して、応答を取得する
    generator_output = tripal_gpt.get_response(user_input=user_chat)
    # 応答をJSON形式に変換する
    # res_json = jsonify({'response': res})
    # return res_json
    # return Response(res, mimetype='text/event-stream')

    # Responseオブジェクトを作成する
    response = make_response(generator_output)
    response.mimetype = 'text/event-stream'

    return response


if __name__ == '__main__':
    app.run(debug=True)
