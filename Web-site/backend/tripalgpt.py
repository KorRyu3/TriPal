import openai
import os
from operator import itemgetter
from dotenv import load_dotenv

# LangChainのモジュールをインポート
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import Tool
from langchain.agents import AgentExecutor


# Function Callingで利用する関数
# 入力の二乗を返す関数
def square(x):
    x = int(x)
    return x ** 2





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
            # system pronptの定義
            ("system", system_prompt),
            # 履歴を取得
            MessagesPlaceholder(variable_name="history"),
            # userの入力
            ("human", "{input}"),
            # agent機能
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # メモリーの初期化
        self.memory = ConversationBufferMemory(memory_key="history", return_messages=True)

        # function callingで利用するツールの初期化
        self.tools = [
            Tool(
                name="Computing_Squares",
                func=square,
                description="二乗の計算をする際に使います。入力は整数のみです。e.g. 2",
            ),
        ]

    
    def cre_agent_exe(self):
        
        # LangChainのLCELを利用して、Chainを作成する
        history = self.memory.load_memory_variables

        # Toolで定義した関数を、Function callingで利用できるように変換する
        model_with_tools = self.model.bind(functions=[format_tool_to_openai_function(t) for t in self.tools])

        agent = {
            
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        # itemgetter("history") は、memory.load_memory_variablesの戻り値の中から、historyの値を取り出す
        # 詳細は"https://python.langchain.com/docs/expression_language/cookbook/memory"を参照
        } | RunnablePassthrough.assign(
            history=RunnableLambda(history) | itemgetter("history")
        ) | self.prompt | model_with_tools | OpenAIFunctionsAgentOutputParser()

        # agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)


        return agent_executor



    # 履歴を保存する
    def _memory_response(self, input):

        # Chainの作成
        chain = self.cre_agent_exe()

        # ユーザーからの入力を取得する
        input = {"input": input}

        # 履歴を元に、Chainを実行する
        res = chain.invoke(input=input)
        output = res["output"]
        # 履歴を保存する
        self.memory.save_context(input, {"output": output})

        return output


    # ユーザーからの入力を取得する
    def get_response(self, input):
        # memory_responseメソッドを呼び出して、応答を取得する
        output = self._memory_response(input=input)

        return output

