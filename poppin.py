from mastodon import Mastodon
from dotenv import load_dotenv
import re
from poppin_db import PoppinDB
import generate_response
import os
import importlib.util
import time
from bs4 import BeautifulSoup

load_dotenv()

# bot_personalitiesフォルダのパス
personalities_directory = "bot_personalities"

# ボットの番号のリストを初期化
bot_nos = []

# ボットのタイプのリストを初期化
bot_types = []

last_notification_id = None

# bot_personalitiesフォルダ内の性格ファイルを取得
for filename in os.listdir(personalities_directory):
    if filename.endswith(".py") and filename != "__init__.py":
        # 各性格ファイルからbot_noとbot_typeを取得してリストに追加
        module_path = os.path.join(personalities_directory, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        bot_nos.append(module.bot_no)
        bot_types.append(module.bot_type)

def load_all_personalities(directory):
    personalities = {}

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            personality_name = filename[:-3]
            module_name = f"{directory}.{personality_name}"
            spec = importlib.util.spec_from_file_location(module_name, os.path.join(directory, filename))
            personality_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(personality_module)

            # 必要な変数が定義されているかチェック
            required_variables = ["messages", "bot_type", "bot_message"]
            for var in required_variables:
                if not hasattr(personality_module, var):
                    raise AttributeError(f"{personality_name}.pyに{var}が定義されていません。")

            personalities[personality_name] = personality_module

    return personalities

# メイン処理
def main(notifications):
    global last_notification_id
    # メンションの内容を出力
    new_mentions = False
    for mention in notifications:
        if mention['type'] == 'mention':
            print(f"From: @{mention['account']['username']}")
            print(f"Content: {mention['status']['content']}")
            print("-" * 30)

            soup = BeautifulSoup(mention['status']['content'], 'html.parser')
            message = soup.get_text()
            message = re.sub(r'^@\w+\s+', '', message)

            print(message)
            text = "私の名前は" + mention['account']['display_name'] + "です。" + message
            acct = mention['status']['account']['acct']
            status = mention['status']
            visibility = mention['status']['visibility']

            # PoppinDB クラスを使ってオブジェクトを作成する
            data = PoppinDB(
                account_id=mention['account']['username'], 
                user_name=mention['status']['account']['username'], 
                bot_type=1,
                text=text, 
                message=[], 
                response=""
            )

            # 入力されたテキストがどれかのボットのタイプと一致するかチェックするループ
            for bot_type, bot_no in zip(bot_types, bot_nos):
                if message == bot_type:
                    # テキストがボットのタイプと一致した場合の処理
                    data.bot_type = bot_no
                    data.insert_users()

                    # タイプを切り替えた時のメッセージを取得
                    bot_message = module.bot_message

                    try:
                        mastodon.status_reply(status, bot_message, acct, visibility=visibility)
                    except Exception as e:
                        print('=== エラー内容 ===')
                        print('type:' + str(type(e)))
                        print('args:' + str(e.args))
                        print('e自身:' + str(e))
                    last_notification_id = mention['id']
                    return  # モードを変更した場合はここで処理を終了

            # promptでreplyを生成する
            data.get_users()
            data.get_messages()
            
            reply = ""
            reply = generate_response.generate_response(data.message, data.bot_type, text).lstrip()
            data.response = reply

            print(reply)
            # リプライする
            try:
                mastodon.status_reply(to_status=status,
                        status=reply,
                        visibility=visibility)
            except Exception as e:
                print('=== エラー内容 ===')
                print('type:' + str(type(e)))
                print('args:' + str(e.args))
                print('e自身:' + str(e))

            # 今回の内容を保存する
            data.db_insert()
                        
            # 最新の通知IDを記録
            last_notification_id = mention['id']
            new_mentions = True

    # 新しい通知が1件もない場合はメッセージを表示
    #if not new_mentions:
    #    print("新しい通知はありません")

    # last_notification_idをファイルに保存
    with open(data_file, "w") as f:
        f.write(str(last_notification_id))

mastodon = Mastodon(access_token = 'clientcred.txt')
print("起動しました")

# last_notification_idを永続化するファイルパス
data_file = "last_notification_id.txt"

# ファイルが存在する場合は読み込む
if os.path.exists(data_file):
    with open(data_file, "r") as f:
        last_notification_id = f.read()
else:
    last_notification_id = None

while True:
    # 自分宛の通知を取得 (差分取得)
    notifications = mastodon.notifications(min_id=last_notification_id)
    main(notifications)
    time.sleep(1)