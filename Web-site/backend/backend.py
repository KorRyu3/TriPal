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
        system_prompt = """
            あなたは、ユーザーの質問に答えるAIアシスタントです。
        """
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # メモリーの初期化
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    # Chainの作成
    def create_chain(self):
            
        # LangChainのLCELを利用して、Chainを作成する
        history = self.memory.load_memory_variables
        # itemgetter("history") は、memory.load_memory_variablesの戻り値の中から、historyの値を取り出す
        # 詳細は"https://python.langchain.com/docs/expression_language/cookbook/memory"を参照
        chain = RunnablePassthrough.assign(
            history=RunnableLambda(history) | itemgetter("history")
        ) | self.prompt | self.model

        return chain


    # 履歴を保存する
    def memory_response(self, user_res):

        # Chainの作成
        chain = self.create_chain()

        # ユーザーからの入力を取得する
        inputs = {"input": user_res}
        # 履歴を元に、Chainを実行する
        res = chain.invoke(input=inputs)
        # 履歴を保存する
        self.memory.save_context(inputs, {"output": res.content})

        return res.content


    # ユーザーからの入力を取得する
    def get_response(self, user_chat):
        # memory_responseメソッドを呼び出して、応答を取得する
        self.ai_response = self.memory_response(user_chat)
        return self.ai_response

