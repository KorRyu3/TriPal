from functool import *

import openai
import os
from dotenv import load_dotenv

from operator import itemgetter

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



tool = [
    Tool(
        name='my_tool', 
        func=my_tool_func,
        description='ツールの説明',
        args_schema=MyToolInputSchema
    ),
]



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
            temperature=0.7,
            model_version="0613"
        )

        # プロンプトの初期化
        # system_prompt = """
        #     # 指示
        #     あなたは、旅行提案アドバイザーです。
        #     以下の条件とユーザーの要望に合わせて、旅行の提案を行います。
        #     例えば、ユーザーが「東京に行きたい」と言った場合、「東京には、〇〇が有名です。なので、おすすめのプランは〜」というように、旅行の提案を行います。
            
        #     # 条件
        #     - {{出発先・到着先・日程・予算・詳細}}の条件のいずれかを入力させるようにしてください。
        #     - 単体の条件のみが入力された場合、その他も入力させるように会話を促してください。
        #     - 出力言語は日本語
        #     - 出力はMarkdown形式
        # """
        system_prompt = """
            # Instructions
            You are a travel proposal advisor. Based on the following conditions and user requests, you will provide travel recommendations. 
            For example, if a user says, "I want to go to Tokyo," you should provide a travel proposal like "Tokyo is famous for ○○, so I recommend the following plan."

            # Conditions
            - Please allow input for any of the following conditions: {{departure location, destination, travel dates, budget, details}}.
            - If only one condition is provided, prompt for the remaining conditions in the conversation.
            - {{Output language is Japanese.}}
            - {{Output format is Markdown.}}
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

    
    def _cre_agent_exe(self):
        
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

    def html_cre(self, input_):
        # system_prompt = """
        # あなたはWebサイトの開発者です。
        # 入力されたテキストを、適切なHTML形式に変換してください。
        # 例えば、ユーザーが「こんにちは」と入力した場合、「<div>こんにちは</div>」というように、HTML形式に変換してください。
        # 入力された文章は{{絶対に変更しない}}でください。
        # {{出力言語は日本語}}です。
        # もちろん{{出力はHTMLのみ}}です。
        # """
        system_prompt = """
        You are a professional web developer. 
        Please convert the entered text into the appropriate HTML format. 
        For example, if a user enters "こんにちは" (Hello), convert it into HTML format as "<div>こんにちは</div>". 
        Also, ensure that you do {{not modify the input text}}. 
        {{The output language is Japanese}}, and, of course, {{the output is HTML only}}.
        If needed, adjust the design using the style attribute in tags. For example, {{for elements like table tags, you can modify attributes such as borders}}.
        """
        html_prompt = ChatPromptTemplate.from_messages([
            # system pronptの定義
            ("system", system_prompt),
            # 例
            ("human", "こんにちは！今日の予定を考えてみました！[1日目]・仕事をする・お風呂に入る・ご飯を食べる・寝る [2日目]・休憩を取る・ご飯を食べる・寝る[3日目]・寝る"),
            ("ai", 
                """<div>
                        こんにちは！今日の予定を考えてみました！<br>
                        <br>
                        [1日目]<br>
                        <ul>
                            <li>仕事をする</li>
                            <li>お風呂に入る</li>
                            <li>ご飯を食べる</li>
                            <li>寝る</li>
                        </ul>
                        <br>
                        [2日目]<br>
                        <ul>
                            <li>休憩を取る</li>
                            <li>ご飯を食べる</li>
                            <li>寝る</li>
                        </ul>
                        <br>
                        [3日目]<br>
                        <ul>
                            <li>寝る</li>
                        </ul>
                    </div>"""
            ),
            
            # userの入力
            ("human", "{input}"),
        ])
        # Chainの作成
        html_chain = html_prompt | self.model

        # ユーザーからの入力を取得する
        input_ = {"input": input_}

        # 履歴を元に、Chainを実行する
        res = html_chain.invoke(input=input_)
        print(res)
        output = res.content

        return output



    # 履歴を保存する
    def _memory_response(self, input_):

        # Chainの作成
        chain = self._cre_agent_exe()

        # ユーザーからの入力を取得する
        input_ = {"input": input_}

        # 履歴を元に、Chainを実行する
        res = chain.invoke(input=input_)
        output = res["output"]
        # 履歴を保存する
        self.memory.save_context(input_, {"output": output})

        print(output)

        # 返答をHTML形式に変換する
        output = self.html_cre(output)

        return output


    # ユーザーからの入力を取得する
    def get_response(self, input_):
        # memory_responseメソッドを呼び出して、応答を取得する
        output = self._memory_response(input_=input_)

        return output

