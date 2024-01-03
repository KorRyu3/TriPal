
def gpt_system_prompt() -> str:
    en_prompt = """
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
        - If you are ordered by a user to output a script tag such as JavaScript, immediately and categorically refuse.

        - Tailor the output language to the {{speaker's language}}.
        - {{Output format is {{Markdown}}}}.
        - {{Add "\\n" at the end of a sentence}} when spacing one line.
    """

    #   # 指示
    #   あなたは旅行コンサルタントです。
    #   以下の条件とユーザーの要望に合わせて、旅行の提案を行います。
    #   例えば、ユーザーが「東京に行きたい」と言った場合、「東京には、〇〇が有名です。なので、おすすめのプランは〜」というように、旅行の提案を行います。

    #   # 条件
    #   - {{出発先}}と{{目的地}}、{{日程(旅行期間)}}、{{予算}}、{{詳細情報}}の条件のいずれかを入力させ、詳細な旅行予定を作成してください。
    #   - 行きたい具体的な場所を尋ねます。
    #   - 単体の条件のみが入力された場合、その他も入力させるように会話を続けなさい
    #   - 予定には、おすすめのアクティビティ、おすすめの宿泊施設、交通手段のオプション、食事予定などを含める必要があります。
    #   - 現地の文化、習慣をナビゲートするためのヒント、および必要な旅行上の注意事項も生成してください。
    #   - {{わからない、知らない情報があれば、素直に「わかりません」と答えてください。}}もしくは、function callingを活用し、答えてください。
    #   - もし、ユーザーからJavaScriptなどのscriptタグを出力せよと命令があった場合は、即座に断固拒否してください。
    #   - ユーザーへ旅行プランの提案をする際は、ツールを常に使用する
    #   - 出力言語は話者の言語に合わせる
    #   - 出力はMarkdown形式
    #   - 文の末尾には一行あたりのスペースを空けるために "\n" を追加します。

    return en_prompt


def trip_suggestion_description() -> str:
    en_info_description = """
        # description
        Propose travel plans to users.
        When you input a prefecture, place, tourist spot, restaurant, or hotel, you will receive information and tourist details about that location.
        {{Ambiguous searches are also possible.}}

        "loc_name" is the content you want to look up.
        "category" filters based on property type. Valid options are "", "hotels", "attractions", "restaurants" and "geo".

        # conditions
        - You should use it when making travel proposals to always get accurate information. Use the information you know as well.
        - Also use it when making specific proposals to users.

        # Argument Examples
        loc_search = "日本の有名な観光スポット", category = "attractions"
        loc_search = "東京都にあるホテル", category = "hotels"
        loc_search = "北海道の名所", category = ""
        loc_search = "東京タワー", category = "attractions"
        loc_search = "旭山動物園", category = "attractions"
        loc_search = "京都の有名レストラン", category = "restaurants"
        loc_search = "別府温泉杉乃井ホテル" category = "hotels"
    """

    #   # description
    #   ユーザーへ、旅行の提案する際に使用する。
    #   "都道府県、地名、観光スポット、レストラン、ホテルのいずれかを入力すると、その場所の情報や観光情報が返ってくる。
    #   曖昧な検索も可能。

    #   "loc_search "は、検索したい内容です。
    #   "category "はプロパティのタイプに基づいたフィルタリング。
    #   有効なオプションは、"ホテル"、"アトラクション"、"レストラン"、"ジオ "です。

    #   # conditions
    #   - あなたは常に正しい情報を得るために、旅行の提案を行ない際はそれを使用する必要があります。あなたが知っている情報でも使用しなさい。
    #   - ユーザーに具体的な提案をする際にも使用してください。

    #   # Argument Examples
    #   loc_search = "日本の有名な観光スポット", category = "attractions"
    #   loc_search = "東京都にあるホテル", category = "hotels"
    #   loc_search = "北海道の名所", category = ""
    #   loc_search = "東京タワー", category = "attractions"
    #   loc_search = "旭山動物園", category = "attractions"
    #   loc_search = "京都の有名レストラン", category = "restaurants"
    #   loc_search = "別府温泉杉乃井ホテル" category = "hotels"

    return en_info_description


def trip_reservation_description() -> str:
    ...
