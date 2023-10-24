import openai
import os
from langchain import LLMChain, PromptTemplate
from langchain.chains import ConversationChain

from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI


from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# ====================================================================================
# API認証情報
# ====================================================================================

# 環境変数をロード
load_dotenv()

# OpenAI API Keyを環境変数から取得
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_BASE")
openai.api_type = os.environ.get("OPENAI_API_TYPE")
openai.api_version = os.environ.get("OPENAI_API_VERSION")


# ====================================================================================
template = \
    """
    あなたは旅行プランを提案する専門家です。
    以下の情報をもとに、旅行プランを提案してください。
    過去の会話履歴はこちらを参照: {history}
    Human: {input}
    AI:
    """

# プロンプトテンプレート
prompt_template = PromptTemplate(
                        input_variables   = ["history", "input"],  # 入力変数 
                        template          = template,              # テンプレート
                        validate_template = True,                  # 入力変数とテンプレートの検証有無
                    )

LLM = AzureChatOpenAI(
            deployment_name = "TriPalGPT",
            temperature       = 0,                  # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
            n                 = 1,                  # いくつの返答を生成するか           
            )

# メモリオブジェクト
memory = ConversationBufferMemory(
                                input_key       = None,      # 入力キー該当の項目名
                                output_key      = None,      # 出力キー該当の項目名
                                memory_key      = 'history', # メモリキー該当の項目名
                                return_messages = True,      # メッセージ履歴をリスト形式での取得有無
                                human_prefix    = 'Human',   # ユーザーメッセージの接頭辞
                                ai_prefix       = 'AI',      # AIメッセージの接頭辞
                            )

# LLM Chain
chain = LLMChain(
                llm     = LLM,             # LLMモデル 
                prompt  = prompt_template, # プロンプトテンプレート
                verbose = True,            # プロンプトを表示するか否か
                memory  = memory,          # メモリ
                )

# 入力メッセージ
message = "適切な旅行プランの提案をお願いします。予算は20,000円以内、出発地は東京、目的地は京都です。"

# LLM Chain実行
result = chain.predict(input=message)

# 出力
print(result)


