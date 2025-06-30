# persona_shield
---
## 概要

Persona Shieldは、SNSへの写真投稿による個人情報や生態認証情報の窃取リスクを軽減するWebアプリケーションです。
アプリのバックグラウンドに生成AI機能を組み込み、SNSへの投稿のフローの一部として投稿チェックをすることができます。
---
## アプリの起動方法

1. `main`ディレクトリに移動します。
2. 以下を実行し、環境変数を設定します。Azure OpenAIのAPIが必要です。
```bash
$env:AZURE_OPENAI_ENDPOINT = "YOUR_AZURE_OPENAI_ENDPOINT"
$env:AZURE_OPENAI_API_KEY = "YOUR_AZURE_OPENAI_API_KEY"
```
3. Twitterへの投稿も紐づけたい場合は、`env`ファイルの中身を適切なAPIキーなどに置き換えてください。
4. 以下を実行してWebアプリケーションを起動します。
```bash
streamlit run main.py
```
---
## アプリの使い方
詳しくは動画をご覧ください。
https://github.com/user-attachments/assets/12c61339-2af1-4cf8-ba77-2eccff2ab607

1. 投稿文を入力する。
2. 投稿予定の写真をファイルアップローダにアップロードする。
3. 「投稿」ボタンを押す。
4. 気を付けるべきリスクが表示される。
5. これらのリスクを踏まえて、「Post Anyway」か「Cancel」を選択する。
   - 「Post Anyway」：`env`ファイルに紐づけられたTwitterアカウントから投稿が行われる。
   - 「Cancel」：投稿せずに終了する。
