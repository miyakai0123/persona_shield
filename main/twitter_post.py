import requests
from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth1


def twitter_post(str):
    """
    Twitterにポストする関数

    Args:
    - str (str): ツイートするテキスト
    Returns:
    - None: ツイートの結果をコンソールに表示
        - .envファイルがない場合はその旨を表示して終了
    """
    if load_dotenv():  # .envファイルを読み込む
        API_KEY = os.getenv("API_KEY")
        API_SECRET = os.getenv("API_SECRET")
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
        
        auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        url = "https://api.twitter.com/2/tweets"
        
        # POSTリクエスト
        response = requests.post(
            url,
            auth=auth,
            json={"text": str}
        )
        
        # 結果表示
        if response.status_code == 201:
            print("✅ ツイート成功！")
            print("Tweet ID:", response.json()["data"]["id"])
        else:
            print("❌ ツイート失敗:", response.status_code)
            print(response.text)
    else: 
        print("""
実際にTwitterにポストするに.envファイルにTwitter API KeyとToken を設定してください。
ツイートする代わりに、ここに本文を表示します

""")
        print(str)
        exit(1)
        
if __name__ == "__main__":
    # ツイートするテキストを指定
    tweet_text = "Hello, world! This is a test tweet from Python script."
    # ツイートを実行
    twitter_post(tweet_text)