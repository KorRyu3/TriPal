import logging
import os
from datetime import datetime
from logging import FileHandler, Formatter, StreamHandler, getLogger
from typing import AsyncGenerator, AsyncIterator

import pytz
from dotenv import find_dotenv, load_dotenv
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool, ToolException
from langchain_core.tracers import RunLogPatch
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import AzureChatOpenAI

from azure_sql_db import insert_conversation_history
from func_call_tools.reservations import TravelReservationSchema, get_reserve_location
from func_call_tools.suggestions import TravelProposalSchema, get_trip_suggestions_info
from llm_prompts import (
    get_system_prompt,
    get_trip_reservation_desc,
    get_trip_suggestion_desc,
    prompt_injection_defense,
)

# ---------- 初期化処理 ---------- #
# directoryをsrcに変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# 環境変数をロード
load_dotenv(find_dotenv())
# ---Logの出力---
logger = getLogger(__name__)
logger.setLevel(logging.ERROR)
# handlerの設定
# StreamHandler
stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s %(message)s"))
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)
# FileHandler
file_handler = FileHandler(filename="logs/tripalgpt.log")
file_handler.setFormatter(Formatter("[%(levelname)s] %(asctime)s\n" + "%(message)s"))
file_handler.setLevel(logging.ERROR)
logger.addHandler(file_handler)

# Time Zoneを設定
TOKYO_TIMEZONE = pytz.timezone("Asia/Tokyo")
# ------------------------------- #


class TriPalGPT:
    """
    Azure Chat OpenAI による旅行の計画を提案するクラス
    """

    def __init__(self, token_id: int) -> None:
        self._token_id = token_id

        self._model_16k = AzureChatOpenAI(
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),  # API key
            deployment_name=os.environ.get(
                "AZURE_OPENAI_API_DEPLOYMENT"
            ),  # deployment name
            azure_endpoint=os.environ.get("AZURE_OPENAI_API_BASE"),  # endpoint (URL)
            openai_api_version=os.environ.get(
                "AZURE_OPENAI_API_VERSION", default="2024-02-15-preview"
            ),  # API version
            model_name="gpt-35-turbo-16k",
            openai_api_type="azure",  # API type
            model_version="1.0.0",
            temperature=1.0,
            streaming=True,
        )

        self._prompt = ChatPromptTemplate.from_messages(
            [
                # prompt injection対策
                ("system", prompt_injection_defense()),
                # system promptの定義
                ("system", get_system_prompt()),
                # 履歴を取得
                MessagesPlaceholder(variable_name="chat_history"),
                # userの入力
                ("human", "{input}"),
                # agent機能
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # メモリーの初期化
        self._memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # function callingで利用するツールの初期化
        # Toolsのエラーハンドリングする関数
        def _handle_error(error: ToolException) -> str:
            error_msg = f"""
                [ToolException]
                The following errors occurred during tool execution:\n
                {error.args[0]}\n
                Please try another tool or let the user type again!
            """
            # errorをログに出力
            logger.exception(error_msg)

            return error_msg

        self._tools = [
            # 提案機能
            StructuredTool.from_function(
                name="Location_Information",
                func=get_trip_suggestions_info,
                description=get_trip_suggestion_desc(),
                args_schema=TravelProposalSchema,
                handle_tool_error=_handle_error,
            ),
            StructuredTool.from_function(
                name="Reservation_Information",
                func=get_reserve_location,
                description=get_trip_reservation_desc(),
                args_schema=TravelReservationSchema,
                handle_tool_error=_handle_error,
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
        model_with_tools = self._model_16k.bind(
            functions=[convert_to_openai_function(t) for t in self._tools]
        )

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
                # history(x)["chat_history"]は、memory.load_memory_variablesの戻り値の中から、historyの値を取り出す
                # 詳細は"https://python.langchain.com/docs/expression_language/cookbook/memory"を参照
                "chat_history": lambda x: history(x)["chat_history"],
            }
            | self._prompt
            | model_with_tools
            | OpenAIFunctionsAgentOutputParser()
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self._tools,
            # verbose=True,  # 途中経過を表示(debug用)
        )

        return agent_executor

    # streaming可能なgeneratorを返す
    def _fetch_astream_log(self, user_input: str) -> AsyncIterator[RunLogPatch]:
        """
        ユーザーの入力をLLMに渡して、streaming形式のlogを取得する。

        :param user_input: ユーザーからの入力
        """
        # Chainの作成
        chain = self._create_agent_executor()
        user_input_dict = {"input": user_input}

        try:
            # Chainを実行する。出力形式はStreaming
            return chain.astream_log(input=user_input_dict)
        except Exception as e:
            # エラーをログに出力
            logger.exception(f"[Chain Error] chainを実行出来ませんでした。\n{e}")

            raise RuntimeError("chainを実行出来ませんでした。 Please try again!") from e

    # 履歴を保存する
    def _save_memory(self, user_input: str, final_output: str) -> None:
        """
        ユーザーの入力と最終的な出力を履歴に保存する。

        :param user_input: ユーザーからの入力
        :param final_output: 保存する最終的な出力
        """
        self._memory.save_context({"input": user_input}, {"output": final_output})

    # 応答を整形する
    def _format_astream_log(self, data: RunLogPatch) -> None | dict[str, str]:
        """
        streamingで出力されるlogを綺麗な形に整形し、必要な情報のみを取得する。

        1 token(例えば"あ"や"う"など)のみを取得するために、logにあるpathを使って、その識別しています。
        また、関係のないlogや、空白のtokenはNoneを返すようにしています。

        :param data: streamingで出力されるlog
        """
        dict_data: dict = data.ops[0]
        path: str = dict_data["path"]

        required_pattern = "/logs/AzureChatOpenAI"
        streaming_pattern = "/streamed_output_str/-"
        final_pattern = "/final_output"

        # pathには /logs/AzureChatOpenAI/streamed_output_str/- などが入っています。
        # なぜ分けて判定しているかというと、AgentExecutorで複数回thinkingが行われると、このpathが動的に変更されるため、静的で変わらない部分で判定しています。
        # 例) /logs/AzureChatOpenAI:2/streamed_output_str/- など  (:2の部分が動的に変わる)
        if required_pattern not in path:
            return None
        if streaming_pattern in path:
            streamed_res: str = dict_data["value"]
            if streamed_res != "":
                return {"stream_res": streamed_res}
        # こちらも同様
        elif final_pattern in path:
            final_res: str | None = dict_data["value"]
            final_res_str: str = (
                final_res["generations"][0][0]["text"] if final_res else ""
            )
            if final_res_str != "":
                return {"final_output": final_res_str}
        # patternに合致しない場合はNoneを返す
        return None

    # 応答を取得する
    async def get_async_generator_output(
        self, user_input: str
    ) -> AsyncGenerator[str, None]:
        """
        ユーザーの入力をLLMに渡して、streaming形式のasync generatorを取得する。

        :param user_input: ユーザーからの入力
        """
        # memory_responseメソッドを呼び出して、応答を取得する
        generator_response = self._fetch_astream_log(user_input=user_input)

        async for res in generator_response:
            format_res = self._format_astream_log(res)

            if format_res is None:
                # 関係のないlogや、空白のtokenは無視
                continue

            if format_res.get("final_output") is not None:
                final_output = format_res["final_output"]
                # 履歴を保存
                self._save_memory(user_input, final_output)

                # 現在の日時を東京タイムゾーンで取得
                current_timestamp = datetime.now(TOKYO_TIMEZONE)

                # 履歴を保存
                insert_conversation_history(
                    token_id=self._token_id,
                    input_text=user_input,
                    output_text=final_output,
                    conversation_timestamp=current_timestamp,
                )

                break

            yield format_res["stream_res"]


# import asyncio
# async def main():
#     async for output in TriPalGPT("aaaaa").get_async_generator_output(user_input="北海道のアクティビティを教えて"):
#         print(output, end="")

# if __name__ == "__main__":
#     asyncio.run(main())
