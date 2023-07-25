import openai
import os
from dotenv import load_dotenv
import importlib

# bot_personalitiesフォルダのパス
personalities_directory = "bot_personalities"

bot_messages_list = []

def load_messages(bot_no):
    # bot_personalitiesフォルダ内の性格ファイルを取得
    for filename in os.listdir(personalities_directory):
        if filename.endswith(".py") and filename != "__init__.py":
            # モジュールを動的にインポート
            module = importlib.import_module(f"{personalities_directory}.{filename[:-3]}")

            # モジュールの中身を調べる
            messages = getattr(module, "messages", [])
            get_bot_no = getattr(module, "bot_no", 0)
            if get_bot_no == bot_no:
                return messages
    return None

def generate_response(message, bot_no, text):
    try:
        load_dotenv()
        openai.api_key = os.environ["OPENAI_API_KEY"]

        messages = load_messages(bot_no)
        print(messages)
        messages = messages + message
        messages.append({"role": "user", "content": text})

        print(messages)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(str(e))
        response = "現在OpenAIのAPIサーバー側で"
        response += "問題が発生しているようです。"
        response += "しばらく時間を置いてから"
        response += "やり直してほしいです。申し訳ないです。"
        # エラーが発生した場合は、エラーメッセージを返す
        return response
