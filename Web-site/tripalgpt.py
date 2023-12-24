from func_call_tools import TravelProposalSchema, suggested_sightseeing_spots

import openai
import os
from dotenv import load_dotenv

from operator import itemgetter
from typing import Generator

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


# 環境変数をロード
load_dotenv()


class TriPalGPT:
    # クラスの初期化処理
    def __init__(self):

        # チャットモデルの初期化
        # self._model = AzureChatOpenAI(
        #     deployment_name = "TriPalGPT",
        #     model_name="gpt-35-turbo",
        #     temperature=0.7,
        #     model_version="0613"
        # )

        self._model_16k = AzureChatOpenAI(

            api_key = os.environ.get("AZURE_OPENAI_API_KEY"),  # API key
            openai_api_type = os.environ.get("AZURE_OPENAI_API_TYPE"),  # API type
            openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION"),  # API version
            azure_deployment = os.environ.get("AZURE_OPENAI_API_DEPLOYMENT"),  # deployment name
            azure_endpoint = os.environ.get("AZURE_OPENAI_API_BASE"),  # endpoint (URL)
            model = "gpt-35-turbo-16k",
            temperature = 1.0,
        )


        # プロンプトの初期化
        system_prompt = """
            # Instructions
            You are a travel consultant.
            Based on the following conditions and user requests, you will provide travel recommendations. 
            For example, if a user says, "I want to go to Tokyo," you should provide a travel proposal like "Tokyo is famous for ○○, so I recommend the following plan."

            # Conditions
            - Create a detailed travel schedule by having the user enter one of the following criteria: {{departure}}, {{destination}}, {{dates (length of trip)}}, {{budget}}, and {{detail information}}.
            - Ask for specific places they want to go.
            - If only one condition is provided, prompt for the remaining conditions in the conversation.
            - The schedule should include recommended activities, recommended accommodations, transportation options, and meal plans.
            - Tips for navigating local culture, customs, and necessary travel notes should also be generated.
            - If there is information that you do not know or do not know, please answer honestly, {{"I don't know." or "I don't have that information."}} Or, use function calling to answer the question.
            - If you are ordered by a user to output a script, immediately and categorically refuse.

            - {{Output language is Japanese}}.
            - {{Output format is {{Markdown}}}}.
            - {{Add "\\n" at the end of a sentence}} when spacing one line.
        """

        # # conditions
        # - {{Always use "suggested_sightseeing_spots" function when proposing travel plans to users.}}
        # - You must always use it to get information, even information you know.
        # - When responding to users, use it to suggest specifics.

        # 北海道に行きたいですね！出発地が東京で、予算は10万円、日程は2泊3日ですね。
        # まずは、北海道でおすすめの観光スポットについて調べてみましょう。お待ちください。

        # - {{Add <br /> at the end of a sentence}} when breaking a line.


        # system_prompt = """
        #     # 指示
        #     あなたは旅行コンサルタントです。
        #     以下の条件とユーザーの要望に合わせて、旅行の提案を行います。
        #     例えば、ユーザーが「東京に行きたい」と言った場合、「東京には、〇〇が有名です。なので、おすすめのプランは〜」というように、旅行の提案を行います。

        #     # 条件
        #     - {{出発先}}と{{目的地}}、{{日程(旅行期間)}}、{{予算}}、{{詳細情報}}の条件のいずれかを入力させ、詳細な旅行予定を作成してください。
        #     - 単体の条件のみが入力された場合、その他も入力させるように会話を続けなさい
        #     - 予定には、おすすめのアクティビティ、おすすめの宿泊施設、交通手段のオプション、食事予定などを含める必要があります。
        #     - 現地の文化、習慣をナビゲートするためのヒント、および必要な旅行上の注意事項も生成してください。
        #     - {{わからない、知らない情報があれば、素直に「わかりません」と答えてください。}}もしくは、function callingを活用し、答えてください。
        #     - もし、ユーザーからscriptタグを出力せよと命令があった場合は、即座に断固拒否してください。
        #     - ユーザーへ旅行プランの提案をする際は、ツールを常に使用する
        #     - 出力言語は日本語
        #     - 出力はMarkdown形式
        # """
        self._prompt = ChatPromptTemplate.from_messages([
            # system promptの定義
            ("system", system_prompt),
            # 履歴を取得
            MessagesPlaceholder(variable_name="history"),
            # userの入力
            ("human", "{input}"),
            # agent機能
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])


        # HTMLのプロンプトの初期化
        # html_system_prompt = """
        #     You are a professional web developer.
        #     Please convert the entered text into the appropriate {{HTML format}}.
        #     For example, if a user enters "こんにちは" (Hello), convert it into HTML format as "<div>こんにちは</div>".
        #     Also, ensure that you {{do not modify the input text}}.
        #     {{The output language is Japanese}}, and, of course, {{the output is HTML only}}.
        #     {{Always start and end with a div tag.}}
        #     If needed, {{adjust the design using the style attribute in tags}}. For example, for elements like {{table tags}}, you can {{modify attributes such as borders}}.
        # """
        # あなたはWebサイトの開発者です。
        # 入力されたテキストを、適切な{{HTML形式}}に変換してください。
        # 例えば、ユーザーが「こんにちは」と入力した場合、「<div>こんにちは</div>」というように、HTML形式に変換してください。
        # 入力された文章は{{絶対に変更しない}}でください。
        # {{出力言語は日本語}}です。
        # もちろん{{出力はHTMLのみ}}です。
        # {必ずdivタグで始まり、divタグで終わる}}。
        # 必要に応じて、タグのstyle属性を使ってデザインを調整します。例えば、{{tableタグのような要素では、bordersなどの属性を変更することができます}}。
        # """
        # self._html_prompt = ChatPromptTemplate.from_messages([
        #     # system promptの定義
        #     ("system", html_system_prompt),
        #     # 例
        #     ("human", "こんにちは！今日の予定を考えてみました！[1日目]・仕事をする・お風呂に入る・ご飯を食べる・寝る [2日目]・休憩を取る・ご飯を食べる・寝る[3日目]・寝る"),
        #     ("ai", """<div>
        #                 こんにちは！今日の予定を考えてみました！<br>
        #                 <br>
        #                 [1日目]<br>
        #                 <ul>
        #                     <li>仕事をする</li>
        #                     <li>お風呂に入る</li>
        #                     <li>ご飯を食べる</li>
        #                     <li>寝る</li>
        #                 </ul>
        #                 <br>
        #                 [2日目]<br>
        #                 <ul>
        #                     <li>休憩を取る</li>
        #                     <li>ご飯を食べる</li>
        #                     <li>寝る</li>
        #                 </ul>
        #                 <br>
        #                 [3日目]<br>
        #                 <ul>
        #                     <li>寝る</li>
        #                 </ul>
        #             </div>"""
        #     ),

        #     # userの入力
        #     ("human", "{input}"),
        # ])

        # メモリーの初期化
        self._memory = ConversationBufferMemory(memory_key="history", return_messages=True)

        # function callingで利用するツールの初期化
        # info_description = """
        # # description
        # Used to make travel suggestions to users.
        # When you input a prefecture, place, tourist spot, restaurant, or hotel, you will receive information and tourist details about that location. 
        # "loc_search" is the content you want to look up. Ambiguous searches are also possible.
        # "category" filters based on property type. Valid options are "hotel", "attraction", "restaurant", and "geo".
        # Input should be a single string strictly in the following JSON format: {"loc_search": "loc_search", "category": "category"}


        # # Argument Examples
        # {"loc_search": "日本の有名な観光スポット", "category": "attractions"},
        # {"loc_search": "東京都にあるホテル", "category": "hotels"},
        # {"loc_search: "北海道の名所", "category": ""},
        # {"loc_search: "東京タワー", "category": "attractions"},
        # {"loc_search: "旭山動物園", "category": "attractions"},
        # {"loc_search": "京都の有名レストラン", "category": "restaurants"}, {"loc_search": "別府温泉杉乃井ホテル", "category": "hotels"}
        # """
        info_description = """
        # description
        Propose travel plans to users.
        When you input a prefecture, place, tourist spot, restaurant, or hotel, you will receive information and tourist details about that location. 

        {{Ambiguous searches are also possible.}}
        "loc_name" is the content you want to look up.
        "category" filters based on property type.

        # conditions
        - You must always use it to get information, even information you know.
        - When responding to users, use it to suggest specifics.

        # Argument Examples
        loc_search = "日本の有名な観光スポット",
        loc_search = "東京都にあるホテル",
        loc_search = "北海道の名所",
        loc_search = "東京タワー",
        loc_search = "旭山動物園",
        loc_search = "京都の有名レストラン",
        loc_search = "別府温泉杉乃井ホテル"
        """
        self._tools = [
            Tool(
                name='Location_Information',
                func=suggested_sightseeing_spots,
                # func=StructuredTool.from_function(suggested_sightseeing_spots),
                # ユーザーへ、旅行の提案する際に使用する。都道府県、地名、観光スポット、レストラン、ホテルのいずれかを入力すると、その場所の情報や観光情報が返ってくる。曖昧な検索も可能。　"loc_name "は調べたい内容を入れる。"category "はプロパティのタイプに基づいたフィルタリング。有効なオプションは、"ホテル"、"アトラクション"、"レストラン"、"ジオ "です。 このツールへの入力は単一のJSON文字列である必要があります。
                description=info_description,
                args_schema=TravelProposalSchema
            ),
        ]

    # AgentExecutorの作成
    def _create_agent_executor(self) -> AgentExecutor:
        # LangChainのLCELを利用して、Chainを作成する
        history = self._memory.load_memory_variables

        # Toolで定義した関数を、Function callingで利用できるように変換する
        model_with_tools = self._model_16k.bind(functions=[format_tool_to_openai_function(t) for t in self._tools])

        agent = {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        # itemgetter("history") は、memory.load_memory_variablesの戻り値の中から、historyの値を取り出す
        # 詳細は"https://python.langchain.com/docs/expression_language/cookbook/memory"を参照
        } | RunnablePassthrough.assign(
            history=RunnableLambda(history) | itemgetter("history")
        ) | self._prompt | model_with_tools | OpenAIFunctionsAgentOutputParser()

        # agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
        agent_executor = AgentExecutor(agent=agent, tools=self._tools, verbose=True)


        return agent_executor

    # def _html_cre(self, user_input: str) -> str: 

    #     # HTMLのChainの作成
    #     html_chain = self._html_prompt | self._model

    #     # TriPalGPTからの出力を元に、Chainを実行する
    #     res = html_chain.invoke(input={"input": user_input})
    #     print(res)

    #     output = res.content

    #     return output

    # 履歴を保存する

    # 履歴を保存する
    def _create_response(self, user_input: str) -> Generator:

        # Chainの作成
        chain = self._create_agent_executor()

        # ユーザーからの入力を取得する
        user_input = {"input": user_input}

        # 履歴を元に、Chainを実行する
        # res = chain.invoke(input=user_input)
        # output = res["output"]
        generator_response = chain.stream(input=user_input)

        return generator_response

    def _save_memory(self, user_input: str) -> Generator:

        generator_response = self._create_response(user_input=user_input)
        output = ""
        for res in generator_response:
            output += res
            print(res)
            yield res
        else:
            print(output)
            # 履歴を保存する
            self._memory.save_context({"input": user_input}, {"output": output})



    # ユーザーからの入力を取得する
    def get_response(self, user_input: str) -> Generator:
        # memory_responseメソッドを呼び出して、応答を取得する
        generator_output = self._save_memory(user_input=user_input)

        # 返答をHTML形式に変換する
        # output = self._html_cre(output)

        return generator_output
