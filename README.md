# persona_shield
---
## 概要
Persona Shieldは、SNSへの写真投稿による個人情報や生態認証情報の窃取リスクを軽減するWebアプリケーションです。
アプリのバックグラウンドに生成AI機能を組み込み、SNSへの投稿のフローの一部として投稿チェックをすることができます。
---
## 使い方
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
