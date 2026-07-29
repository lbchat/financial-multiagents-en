"""Global configuration and LLM initialization."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()


def get_llm() -> ChatOpenAI:
    """Returns the configured LLM instance via DeepInfra."""
    api_key = os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPINFRA_API_KEY não encontrada. Configure o arquivo .env")
    return ChatOpenAI(
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=SecretStr(api_key),
        temperature=0.1,
    )
