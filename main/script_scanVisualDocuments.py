"""
このモジュールは、画像ファイルをスキャンしテキスト化するためのユーティリティ関数です。

機能:
- ファイルをBase64形式にエンコードする関数
- 画像ファイルをテキスト化するための関数群
- テキスト化されたファイルをAPIに送信する関数

モジュール変数:
    SUCCESS_CODE (int): 成功時のステータスコード
    FAILURE_CODE (int): 失敗時のステータスコード
    URI_SCAN (str): 画像のテキスト化APIのエンドポイント
    URI_PROGRESS (str): テキスト化進捗確認APIのエンドポイント
    URI_RESULT (str): テキスト化結果取得APIのエンドポイント
    POLLING_INTERVAL (int): ポーリング時の待機時間（秒）
    FILE_INTERVAL (int): 複数ファイルを処理する際のファイル間の待機時間（秒）
    CERT (str or bool): SSL証明書の指定

関数:
    encode_file_to_base64(file_path)
        ファイルをBase64エンコードします。

    scan(api_base_url, auth_token, file_path, model)
        画像ファイルをテキスト化処理のためにAPIに送信します。

    get_progress(api_base_url, request_id, auth_token)
        テキスト化処理の進捗状況を確認します。

    get_result(api_base_url, request_id, auth_token)
        テキスト化処理の結果を取得します。

    write_file(result, filename)
        テキスト化結果をMarkdownファイルとして保存します。

    scan_file(file_path, api_base_url, auth_token, model)
        画像ファイルをスキャンしてテキスト形式に変換します。
"""

import os                            # OS関連の機能
import sys                           # Pythonのインタプリタ制御
import base64                        # バイナリデータのエンコード・デコード
import requests                      # HTTPリクエストを扱うライブラリ
import json                          # JSON形式のデータを扱うためのライブラリ
import traceback                     # エラー発生時のスタックトレースを取得・表示
import time                          # 時間関連の機能
from datetime import datetime        # 日付と時刻を扱うためのライブラリ
from zoneinfo import ZoneInfo        # タイムゾーン情報の取得・操作

import utils                         # utilsモジュール

# 成功時と失敗時(デフォルト)の返すコードをグローバル変数として定義
SUCCESS_CODE = 0 # 成功時のステータスコード
FAILURE_CODE = 1 # 失敗時のステータスコード

# 処理時の設定変数の定義
POLLING_INTERVAL = 10 # ポーリング時の待機時間（秒）
FILE_INTERVAL = 10 # 複数ファイルを処理する際のファイル間の待機時間（秒）
CERT = True # SSL証明書の指定


def encode_file_to_base64(file_path: str) -> str:
    """
    ファイルをBase64エンコードします。

    Args:
        file_path (str): エンコードするファイルのパス。

    Returns:
        str: Base64エンコードされたファイルの文字列。
    """
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("ascii")
    return encoded_string


def scan(
    api_base_url: str,
    auth_token: str,
    file_path: str,
    model: str,
) -> int:
    """
    画像ファイルをテキスト化処理のためにAPIに送信します。

    Args:
        api_base_url (str): APIのベースURL。
        auth_token (str): 認証トークン。
        file_path (str): 画像ファイルのパス。
        model (str): モデル名。

    Returns:
        tuple: (ステータスコード, リクエストID)
               成功時は(0, request_id)、失敗時は(エラーステータスコード, None)を返します。
    """
    encoded_file = encode_file_to_base64(file_path)
    filename = os.path.basename(file_path)


    payload = {
        "file": encoded_file, # Base64エンコードされたファイル
        "filename": filename, # ファイル名
        "model": model,       # モデル名
    }

    headers = {
        "Content-Type": "application/json",      # コンテンツタイプ
        "Authorization": f"Bearer {auth_token}", # 認証トークン
    }

    try:
        # 変換をリクエスト
        response = requests.post(api_base_url + utils.URI_SCAN, headers=headers, json=payload, verify=CERT)
        now = datetime.now(ZoneInfo("Asia/Tokyo"))

        print(f"Processed {filename} at {now}: {response.status_code} {response.text}")

        if response.status_code != 202:
            try:
                data = response.json()
                print("Response Data:", data)
            except json.JSONDecodeError:
                print("Response is not in JSON format")
                print("Response text:", response.text)
            return response.status_code, None  # エラーステータスコードを返す

        data = response.json()
        print(f"request id: {data.get('id')}")
        return SUCCESS_CODE, data.get("id")  # 成功時

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        print(f"[scan] Error scan document: {e}")
        print(f"Error occurred at: {now}")
        return FAILURE_CODE, None  # 失敗時のデフォルトエラーステータスコード


def get_progress(api_base_url: str, request_id: str, auth_token: str):
    """
    テキスト化処理の進捗状況を確認します。

    Args:
        api_base_url (str): APIのベースURL。
        request_id (str): テキスト化リクエストのID。
        auth_token (str): 認証トークン。

    Returns:
        tuple: (ステータスコード, 進捗データ)
               成功時は(0, データ)、失敗時は(エラーステータスコード, None)を返します。
    """
    headers = {
        "Authorization": f"Bearer {auth_token}", # 認証トークン
    }

    try:
        # 進捗状況をリクエスト
        response = requests.get(f"{api_base_url}{utils.URI_PROGRESS}/{request_id}", headers=headers, verify=CERT)

        if response.status_code != 200:
            try:
                data = response.json()
                print("Response Data:", data)
            except json.JSONDecodeError:
                print("Response is not in JSON format")
                print("Response text:", response.text)
            return response.status_code, None  # エラーステータスコードを返す

        data = response.json()
        return SUCCESS_CODE, data  # 成功時

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        print(f"[get_progress] Error scan document: {e}")
        print(f"Error occurred at: {now}")
        return FAILURE_CODE, None  # 失敗時のデフォルトエラーステータスコード


def get_result(api_base_url: str, request_id: str, auth_token: str):
    """
    テキスト化処理の結果を取得します。

    Args:
        api_base_url (str): APIのベースURL。
        request_id (str): テキスト化リクエストのID。
        auth_token (str): 認証トークン。

    Returns:
        tuple: (ステータスコード, 結果データ)
               成功時は(0, データ)、失敗時は(エラーステータスコード, None)を返します。
    """
    headers = {
        "Authorization": f"Bearer {auth_token}",
    }

    try:
        # テキスト化の結果をリクエスト
        response = requests.get(f"{api_base_url}{utils.URI_RESULT}/{request_id}", headers=headers, verify=CERT)

        if response.status_code != 200:
            try:
                data = response.json()
                print("Response Data:", data)
            except json.JSONDecodeError:
                print("Response is not in JSON format")
                print("Response text:", response.text)
            return response.status_code, None  # エラーステータスコードを返す

        data = response.json()
        return SUCCESS_CODE, data  # 成功時

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        print(f"[get_result] Error scan document: {e}")
        print(f"Error occurred at: {now}")
        return FAILURE_CODE, None  # 失敗時のデフォルトエラーステータスコード


def write_file(result, filename="output"):
    """
    テキスト化結果をMarkdownファイルとして保存します。

    Args:
        result (dict): テキスト化APIから返された結果データ。
        filename (str, optional): 出力ファイルのベース名。デフォルトは"output"。

    Returns:
        str: 保存されたファイルのパス。
    """
    pages = result["pages"]
    # 出力先のパス
    output_directory = "./output"
    
    # ファイル名から拡張子を除去し、.md拡張子を追加
    output_filename = f"{os.path.splitext(filename)[0]}.md"
    output_path = f"{output_directory}/{output_filename}"

    # ディレクトリが存在しない場合、作成する
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(output_path, "w", encoding="utf-8") as f:
        for page in pages:
            f.write("\n\n".join(chunk["text"] for chunk in page["chunks"]))
    return output_path


def scan_file(
    file_path: str,
    api_base_url: str,
    auth_token: str,
    model: str,
) -> int:
    """
    画像ファイルをスキャンしてテキスト形式に変換します。

    Args:
        file_path (str): 画像ファイルのパス。
        api_base_url (str): APIのベースURL。
        auth_token (str): 認証トークン。
        model (str): モデル。

    Returns:
        tuple: (ステータスコード, 処理済みファイルパス)
               成功時は(0, 処理済みファイルパス, None)、失敗時は(エラーステータスコード, None, requestId)を返します。
    """
    # 画像処理
    status_code, request_id = scan(api_base_url, auth_token, file_path, model)

    if status_code != SUCCESS_CODE:
        print(f"Failed to scan")
        return status_code, None, None

    # ステータス取得
    while True:
        status_code, data = get_progress(api_base_url, request_id, auth_token)
        if status_code != SUCCESS_CODE:
            print(f"Failed to get progress")
            return status_code, None, request_id

        status = data.get("status", "")
        # 進捗状況の出力
        print(f"  status: {status}")
        if status == "completed": # 完了時
            compelted_at = data.get("timestamp", 0)
            # timestampからdatetimeに変換
            compelted_at = datetime.fromtimestamp(compelted_at, ZoneInfo("Asia/Tokyo"))
            print(f"Scanning completed: {file_path} at {compelted_at}")
            break
        if status == "failed": # 失敗時
            failed_at = data.get("timestamp", 0)
            # timestampからdatetimeに変換
            failed_at = datetime.fromtimestamp(failed_at, ZoneInfo("Asia/Tokyo"))
            print(f"Scanning failed: {file_path} at {failed_at}")
            return FAILURE_CODE, None, request_id
        
        # 一定時間待機
        time.sleep(POLLING_INTERVAL)
    
    # 結果取得
    status, result = get_result(api_base_url, request_id, auth_token)
    if status != SUCCESS_CODE:
        print(f"Failed to get result")
        return status, None, request_id
        
    # ファイル名を渡して出力ファイルを作成
    try:
        filename = os.path.basename(file_path)
        output_path = write_file(result, filename)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        print(f"[write_file] Error write file: {e}")
        print(f"Error occurred at: {now}")
        return FAILURE_CODE, None, request_id  # 失敗時のデフォルトエラーステータスコード

    return SUCCESS_CODE, output_path, None  # 全て成功時