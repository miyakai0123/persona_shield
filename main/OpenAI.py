from __future__ import annotations
from langchain_openai import AzureChatOpenAI

def model_init(model_name, temperature=1.0):
    # モデル定義
    api_version = "2024-12-01-preview"
    model = AzureChatOpenAI(
        openai_api_version=api_version,
        azure_deployment=model_name,  # デプロイ名
        temperature=temperature,
    )
    return model
