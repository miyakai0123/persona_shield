import os                           # osライブラリ

# ============================================= 
# Generative AI Cloud 接続設定
# ============================================= 
# APIキー設定
API_KEY = os.getenv("COTOMIAPI_API_KEY")   
# cotomiエンドポイント設定
ENDPOINT_BASE = os.getenv("COTOMIAPI_ENDPOINT")
# OpenAI互換用cotomiエンドポイント設定
ENDPOINT_BASE_OAI = os.getenv("COTOMIAPI_OAI_ENDPOINT")
# エンベディングモデル名
EMB_MODEL = "gpt-4o"
# エンベディングモデル名
SCAN_VISUAL_MODEL = "scan-std-model-v1-jp"
# 履歴を識別するためのユーザID。ご自身の名前かメールアドレスをご記載ください
USER = "nihondenki tarou"

# ============================================= 
# 画像文脈理解 接続設定
# ============================================= 
# 画像のテキスト化APIのエンドポイント
URI_SCAN = "/genai-api/v1/visualDocuments/scanAsync"
# テキスト化進捗確認APIのエンドポイント
URI_PROGRESS = "/genai-api/v1/visualDocuments/scanStatus"
# テキスト化結果取得APIのエンドポイント
URI_RESULT = "/genai-api/v1/visualDocuments/scanResults"

# ============================================= 
# Generative AI Cloud 設定
# ============================================= 
# 管理画面上で登録したインデックス名
REGIST_INDEX = "handson-index"
# 管理画面上で登録したテンプレートのID
# TEMPLATE_ID = ""
# 分割するトークン数を指定
SPLIT_TOKENS = 512