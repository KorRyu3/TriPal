import os
from typing import AsyncIterator,  Union, Dict

from dotenv import load_dotenv
# LangChain
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import Tool, AgentExecutor
# langchain_core
from langchain_core.tracers import RunLogPatch
from langchain_core.tools import StructuredTool

from func_call_tools.suggestions import TravelProposalSchema, suggested_sightseeing_spots
from func_call_tools.reservations import TravelReservationSchema, reserve_location


# 環境変数をロード
load_dotenv()

class TriPalGPT:
    """
        Azure Chat OpenAI による旅行の計画を提案するクラス
    """
    # クラスの初期化処理
    def __init__(self) -> None:
        self._model_16k = AzureChatOpenAI(

            api_key = os.environ.get("AZURE_OPENAI_API_KEY"),  # API key
            openai_api_type = os.environ.get("AZURE_OPENAI_API_TYPE"),  # API type
            openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION"),  # API version
            azure_deployment = os.environ.get("AZURE_OPENAI_API_DEPLOYMENT"),  # deployment name
            azure_endpoint = os.environ.get("AZURE_OPENAI_API_BASE"),  # endpoint (URL)
            model = "gpt-35-turbo-16k",
            temperature = 1.0,
            streaming = True,
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
            MessagesPlaceholder(variable_name="chat_history"),
            # userの入力
            ("human", "{input}"),
            # agent機能
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])


        # メモリーの初期化
        self._memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

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
        """
            LangChainのLCELを利用して、AgentExecutor(Chain)を作成する。

            Tools(Function calling)付きのChainになっています。
        """
        history = self._memory.load_memory_variables

        # Toolで定義した関数を、Function callingで利用できるように変換する
        model_with_tools = self._model_16k.bind(functions=[format_tool_to_openai_function(t) for t in self._tools])

        agent = {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        # itemgetter("history") は、memory.load_memory_variablesの戻り値の中から、historyの値を取り出す
        # 詳細は"https://python.langchain.com/docs/expression_language/cookbook/memory"を参照
        "chat_history": lambda x: history(x)["chat_history"],
        } | self._prompt | model_with_tools | OpenAIFunctionsAgentOutputParser()


        agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self._tools,
                verbose=True  # 途中経過を表示(debug用)
            )

        return agent_executor


    # streaming可能なgeneratorを返す
    def _create_response(self, user_input: str) -> AsyncIterator[RunLogPatch]:
        """
            ユーザーの入力をLLMに渡して、streaming形式のlogを取得する。

            :param user_input: ユーザーからの入力
        """

        # Chainの作成
        chain = self._create_agent_executor()

        # ユーザーからの入力を取得する
        user_input = {"input": user_input}

        # 履歴を元に、Chainを実行する
        # import pdb; pdb.set_trace()
        generator_response = chain.astream_log(input=user_input)
        # print("generator_response: ", generator_response)
        # print("generator_response(type): ", type(generator_response))

        return generator_response

    # 履歴を保存する
    def _save_memory(self, user_input: str, final_output: str) -> None:
        """
            ユーザーの入力と最終的な出力を履歴に保存する。

            :param user_input: ユーザーからの入力
            :param final_output: 保存する最終的な出力
        """
        self._memory.save_context({"input": user_input}, {"output": final_output})

    # 応答を整形する
    def _format_astream_log(self, data: RunLogPatch) -> Union[None, Dict[str, str]]:
        """
            streamingで出力されるlogを綺麗な形に整形し、必要な情報のみを取得する。

            1 token(例えば"あ"や"う"など)のみを取得するために、logにあるpathを使って、その識別しています。
            また、関係のないlogや、空白のtokenはNoneを返すようにしています。

            :param data: streamingで出力されるlog
        """
        dict_data: dict = data.ops[0]
        # print("dict_data: ", dict_data)
        path: str = dict_data["path"]

        required_pattern = "/logs/AzureChatOpenAI"
        streaming_pattern = "/streamed_output_str/-"
        final_pattern = "/final_output"

        print("path: ", path)
        print("-"*50)

        # pathには /logs/AzureChatOpenAI/streamed_output_str/- などが入っています。
        # なぜ分けて判定しているかというと、AgentExecutorで複数回thinkingが行われると、このpathが動的に変更されるため、静的で変わらない部分で判定しています。
        # 例) /logs/AzureChatOpenAI:2/streamed_output_str/- など  (:2の部分が動的に変わる)
        if required_pattern in path and streaming_pattern in path:
            response: str = dict_data["value"]
            if response == "":
                return None
            else:
                return {"stream_res": response}
        # こちらも同様
        elif required_pattern in path and final_pattern in path:
            response: str = dict_data["value"]["generations"][0][0]["text"]
            if response == "":
                return None
            else:
                return {"final_output": response}

        else:
            return None


        # 応答を取得する
    async def get_async_iter_response(self, user_input: str) -> AsyncIterator[str]:
        """
            ユーザーの入力をLLMに渡して、streaming形式のiteratorを取得する。

            :param user_input: ユーザーからの入力"""
        # memory_responseメソッドを呼び出して、応答を取得する
        generator_response = self._create_response(user_input=user_input)

        async for res in generator_response:
            format_res = self._format_astream_log(res)

            if format_res is None:
                # 関係のないlogや、空白のtokenは無視
                continue

            if format_res.get("final_output"):
                final_output = format_res.get("final_output")
                # 履歴を保存
                self._save_memory(user_input, final_output)
                break

            # print("res: ",format_res.get("stream_res"))
            # print("res(type): ", format_res)
            # print("-"*50)

            yield format_res.get("stream_res")



# import asyncio

# async def main():
#     tripal_gpt = TriPalGPT()
#     # print("input: あなたについて教えて")
#     # async for output in tripal_gpt.get_async_iter_response(user_input="日本にいるくまについて教えて"):
#     async for output in tripal_gpt.get_async_iter_response(user_input="hello"):
#         print("output(type): ", type(output), "  output: ", output)

# if __name__ == "__main__":
#     asyncio.run(main())
#     # main()
