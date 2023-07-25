import sqlite3
from contextlib import closing

class PoppinDB:
    dbname = "poppin.db"

    def __init__(self, account_id="", user_name="", bot_type=1, text="", message=[], response=""):
        self.account_id = account_id
        self.user_name = user_name
        self.bot_type = bot_type
        self.text = text
        self.message = message
        self.response = response
        
        try:
            # テーブルが存在しなければ作成する
            with closing(sqlite3.connect(PoppinDB.dbname)) as conn:
                c = conn.cursor()

                sql = """
                    CREATE TABLE IF NOT EXISTS users (
                        account_id TEXT,
                        user_name TEXT,
                        bot_type INTEGER,
                        PRIMARY KEY (account_id)
                    );
                """
                c.execute(sql)
                sql = """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        account_id TEXT NOT NULL,
                        user_name TEXT NOT NULL,
                        bot_type INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT NOT NULL,
                        FOREIGN KEY (account_id) REFERENCES users (account_id)
                    );
                """
                c.execute(sql)
                conn.commit()
        except Exception as e:
            print("データベース接続エラー:", str(e))

    # ユーザー情報を取得する
    def get_users(self):
        try:
            with closing(sqlite3.connect(self.dbname)) as conn:
                c = conn.cursor()
                sql = "SELECT bot_type FROM users WHERE account_id = ?"
                rows = c.execute(sql, [self.account_id]).fetchall()
                for row in rows:
                    if row[0] != "":
                        self.bot_type = row[0]
                        
        except Exception as e:
            print("データベース接続エラー:", str(e))

    # 会話情報を取得する
    def get_messages(self):
        try:
            with closing(sqlite3.connect(self.dbname)) as conn:
                c = conn.cursor()
                sql = "SELECT message, response FROM messages WHERE account_id = ? ORDER BY id DESC LIMIT 3"
                rows = c.execute(sql, [self.account_id]).fetchall()
                messages = list(reversed(rows))
                self.prompt = []
                for row in messages:
                    if row[0] != "":
                        self.message.append({"role": "user", "content": row[0]})
                        self.message.append({"role": "assistant", "content": row[1]})

        except Exception as e:
            print("データベース接続エラー:", str(e))

    def insert_users(self):
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()

            sql = """
            INSERT OR REPLACE INTO users
            (account_id,user_name,bot_type) 
            values (?,?,?)
            """
            words = (self.account_id,self.user_name,self.bot_type)
            c.execute(sql, words)
            conn.commit()

    def db_insert(self):
        with closing(sqlite3.connect(self.dbname)) as conn:
            c = conn.cursor()

            sql = """
            INSERT OR REPLACE INTO users
            (account_id,user_name,bot_type) 
            values (?,?,?)
            """
            words = (self.account_id,self.user_name,self.bot_type)
            c.execute(sql, words)

            sql = """
            INSERT OR REPLACE INTO messages
            (account_id,user_name,bot_type,message,response)
            values (?,?,?,?,?)"""
            words = (self.account_id,self.user_name,self.bot_type, self.text, self.response)
            c.execute(sql, words)

            conn.commit()
