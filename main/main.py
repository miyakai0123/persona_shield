from __future__ import annotations
import streamlit as st              # Webアプリ生成
from openai import OpenAI           # openaiライブラリ
import utils                        # utilsモジュール
from datetime import datetime       # 日付利用
import time                         # 実行時間計測
from PIL import Image               # 画像処理ライブラリ

import tempfile                     # 一時ファイル管理
from pathlib import Path            # ファイルシステムパス操作
import base64                       # Base64エンコード/デコード
from langchain_core.messages import HumanMessage
from langchain.callbacks import get_openai_callback

from twitter_post import twitter_post
from OpenAI import model_init

from script_scanVisualDocuments import scan_file  # 図表文書スキャン用スクリプト

# 成功時と失敗時(デフォルト)の返すコードをグローバル変数として定義
SUCCESS_CODE = 0
FAILURE_CODE = 1

# APIの設定
client = OpenAI(
    api_key=utils.API_KEY,
    base_url=utils.ENDPOINT_BASE_OAI
)

# ボタンのスタイルシート
button_css = """
<style>
div.stButton > button:first-child  {
    display: inline-block;
    width: auto;              /* 必要に応じて幅を自動調整 */
    min-width: 180px;         /* 最小幅を広めに設定 */
    height: auto;
    padding: 0.5em 1em;       /* 上下左右に余白 */
    font-size: 16px;          /* フォントサイズも調整可能 */
    line-height: 1.5em;
    white-space: nowrap;     /* テキストを折り返さない */
    overflow: hidden;        /* はみ出た部分を非表示（optional） */
    text-overflow: ellipsis; /* はみ出た部分を…表示（optional） */
    border-radius: 6px;
}
</style>
"""

st.set_page_config(page_title="Persona Shield", layout="centered")

def process_uploaded_file(api_base_url, auth_token, uploaded_file, model):
    """
    アップロードされたファイルを処理し、画像をテキスト化する

    Args:
        api_base_url (str): APIのベースURL
        auth_token (str): APIにアクセスするための認証トークン
        uploaded_file (UploadedFile): ストリームリットなどからアップロードされたファイル
        model (str): 画像処理に使用するモデル

    Returns:
        str: 処理の成功もしくは失敗メッセージ
    """
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        # ファイルを一時ディレクトリに保存
        temp_file_path = Path(temp_dir) / uploaded_file.name
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 画像テキスト化関数を呼び出し
        status_code, result_path, request_id = scan_file(temp_file_path, api_base_url, auth_token, model)

        if status_code == 0:
            return f"画像が正常に読み込めました"
        else:
            return f"画像読み込みに失敗しました。 Check logs for Request ID: {request_id}"

def make_imagetext(uploaded_file):
    mime_type = uploaded_file.type  # 'image/png'
    uploaded_file.seek(0)  # 念のため先頭に戻す
    image_data = uploaded_file.read()
    encoded = base64.b64encode(image_data).decode("utf-8")
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{encoded}"}
    }

def prior_knowledge(uploaded_file, input_text):
    """
    Parameters:
    - uploaded_files: List[UploadedFile]（例えば Streamlit の st.file_uploader(..., accept_multiple_files=True) で得たもの）

    Returns:
    - List[HumanMessage]
    """
    if uploaded_file is not None:
        image = make_imagetext(uploaded_file)
        message = HumanMessage(
            content=[
                {"type": "text", "text":
                "以下にSNSに投稿予定の「画像」と「文章」を提示します。\n" +
                "まず1行目には、リスクがあるなら 'yes' と、ないなら 'no' とだけ出力します。\n" +
                "2行目以降には、この投稿によって生じる可能性のあるさまざまなリスクについて、日本語で箇条書きで丁寧に洗い出してください。\n" +
                "また、それぞれのリスクに対して「なぜそれがリスクになるのか」「それを避けるにはどうすべきか」という視点から、具体的な対策を添えてください。\n" +
                "以下のチェックリストに掲載されていないリスクを出力する必要はありません。\n" +
                "チェックしていただきたいリスクは以下の通りです：\n" +
                "1. 個人情報・身バレリスク\n" +
                "・画像に移っている場所・輻輳・名札・建物・部屋の背景などから、投稿者の身元が特定される可能性はないか\n" +
                "・文章に含まれる地名・職場・学校・人間関係・行動履歴などから居住地や生活パターンが推測されないか\n" +
                "・投稿に写る他社（特に未成年・家族・友人）のプライバシーが侵害される要素ないか\n" +
                "・指の腹が写っていて指紋を偽造される可能性はないか\n" +
                "2. 誤読・炎上・誤解のリスク\n" +
                "・文章の言い回しに曖昧さ・誤読されやすい表現が含まれていないか\n" +
                "・画像と文章の組み合わせにより、意図と異なる意味や解釈が生まれていないか\n" +
                "・投稿内容が一部の人に不快感・差別的印象・攻撃的印象を与える可能性はないか\n" +
                "・ユーモア・皮肉・風刺が伝わらず、炎上を招くリスクがないか\n" +
                "・投稿するタイミングや文脈により、「空気が読めない」「不適切」と受け取られる懸念がないか\n" +
                f"投稿文：{input_text if input_text else '（投稿文なし）'}"},
                image
            ]
        )
    else:
        message = HumanMessage(
            content=[
                {"type": "text", "text":
                "以下にSNSに投稿予定の「文章」を提示します。\n" +
                "まず1行目には、リスクがあるなら 'yes' と、ないなら 'no' とだけ出力します。\n" +
                "2行目以降には、この投稿によって生じる可能性のあるさまざまなリスクについて、日本語で箇条書きで丁寧に洗い出してください。\n" +
                "また、それぞれのリスクに対して「なぜそれがリスクになるのか」「それを避けるにはどうすべきか」という視点から、具体的な対策を添えてください。\n" +
                "以下のチェックリストに掲載されていないリスクを出力する必要はありません。\n" +
                "チェックしていただきたいリスクは以下の通りです：\n" +
                "1. 個人情報・身バレリスク\n" +
                "・画像に移っている場所・輻輳・名札・建物・部屋の背景などから、投稿者の身元が特定される可能性はないか\n" +
                "・文章に含まれる地名・職場・学校・人間関係・行動履歴などから居住地や生活パターンが推測されないか\n" +
                "・投稿に写る他社（特に未成年・家族・友人）のプライバシーが侵害される要素ないか\n" +
                "・指の腹が写っていて指紋を偽造される可能性はないか\n" +
                "2. 誤読・炎上・誤解のリスク\n" +
                "・文章の言い回しに曖昧さ・誤読されやすい表現が含まれていないか\n" +
                "・画像と文章の組み合わせにより、意図と異なる意味や解釈が生まれていないか\n" +
                "・投稿内容が一部の人に不快感・差別的印象・攻撃的印象を与える可能性はないか\n" +
                "・ユーモア・皮肉・風刺が伝わらず、炎上を招くリスクがないか\n" +
                "・投稿するタイミングや文脈により、「空気が読めない」「不適切」と受け取られる懸念がないか\n" +
                f"投稿文：{input_text if input_text else '（投稿文なし）'}"}
            ]
        )

    return [message]

st.title("Persona Shield")

# カスタムCSSでX風にスタイリング
st.markdown("""
    <style>
    .post-card {
        background-color: #1e1e1e;
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0px 0px 10px #00000080;
    }
    .profile {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    .profile-icon {
        background-color: #888;
        width: 40px;
        height: 40px;
        border-radius: 50%;
    }
    .post-button {
        background-color: #1d9bf0;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 9999px;
        font-weight: bold;
        float: right;
    }
    .char-count {
        color: #888;
        font-size: 12px;
        text-align: right;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# プロフィール風
st.markdown("""
<div class="profile">
    <div class="profile-icon"></div>
    <div><b>@Tech_Drift</b></div>
</div>
""", unsafe_allow_html=True)

# テキストエリア
input_text = st.text_area("投稿文", placeholder="いまどうしてる？", max_chars=140, label_visibility="collapsed")
char_count = len(input_text)

# 画像アップロード
uploaded_file = st.file_uploader("画像を追加", type=["png"], label_visibility="collapsed")
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="プレビュー", use_column_width=True)

# 質問送信ボタンがクリックされたらLLMに質問を要求する
if st.button("投稿", key="post_ready"):
    now = datetime.now()
    file_time = now.strftime("%Y%m%d%H%M%S") + str(int(time.time() % 1 * 1000))

    if uploaded_file is not None:
        # 画像を開く
        image = Image.open(uploaded_file)
        
        api_base_url = "/".join(utils.ENDPOINT_BASE.split("/")[:-2])
        auth_token = utils.API_KEY
        model = utils.SCAN_VISUAL_MODEL

        result_message = process_uploaded_file(api_base_url, auth_token, uploaded_file, model)
        st.write(result_message)

    # VLMの初期化
    llm = model_init("gpt-4o", temperature=1.0)
    messages = prior_knowledge(uploaded_file, input_text)

    with get_openai_callback() as cb:
        res = llm.invoke(messages, config={"max_tokens": 1000})

    # ファイル名に現在日時を付与
    context_file_name = "./debug/output_context_{}.txt".format(file_time)
    # ファイルに書き出す
    with open(context_file_name, "w", encoding="utf8") as f:
        f.write(str(res.content))
    
    # === VLM出力に応じた処理 ===
    output_lines = str(res.content).strip().split("\n")
    first_line = output_lines[0].strip().lower()
    remaining_output = "\n".join(output_lines[1:]).strip()

    if first_line == "yes":
        st.warning("⚠️ 投稿にはリスクがある可能性があります。以下をご確認ください。")
        if remaining_output:
            st.write(remaining_output)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Post anyway"):
                twitter_post(input_text)
        with col2:
            if st.button("Cancel"):
                st.info("🛑 投稿がキャンセルされました")
    elif first_line == "no":
        st.success("✅ 投稿に関する大きな問題点は見つかりませんでした。")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Post", key="post_norisk"):
                twitter_post(input_text)
        with col2:
            if st.button("Cancel"):
                st.info("🛑 投稿がキャンセルされました")
    else:
        st.warning("⚠️ VLMの出力形式が想定と異なります。1行目が 'yes' または 'no' で始まるようにしてください。")