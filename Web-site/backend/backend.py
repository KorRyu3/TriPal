import openai
import os
from operator import itemgetter
from dotenv import load_dotenv

from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


class TriPalGPT:
    # クラスの初期化処理
    def __init__(self):

        # 環境変数をロード
        load_dotenv()

        # OpenAI API Keyを環境変数から取得
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        openai.api_base = os.environ.get("OPENAI_API_BASE")
        openai.api_type = os.environ.get("OPENAI_API_TYPE")
        openai.api_version = os.environ.get("OPENAI_API_VERSION")


        # チャットモデルの初期化
        self.model = AzureChatOpenAI(
            deployment_name = "TriPalGPT",
            model_name="gpt-35-turbo",
            temperature=0.5,
            model_version="0613"
        )

        # プロンプトの初期化
        self.system_prompt = """
            あなたは、ユーザーの質問に答えるAIアシスタントです。
        """
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # メモリーの初期化
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)



