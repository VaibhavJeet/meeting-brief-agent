"""LLM configuration with multi-provider support."""

from functools import lru_cache
from typing import Optional

from langchain_core.language_models import BaseChatModel

from app.core.config import settings


@lru_cache()
def get_llm(temperature: float = 0.1) -> BaseChatModel:
    """Get LLM instance based on configuration.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Ollama (Local models)
    - LlamaCpp (Local GGUF models)
    """
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=temperature,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")

        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            temperature=temperature,
        )

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=temperature,
        )

    elif provider == "llamacpp":
        from langchain_community.llms import LlamaCpp

        if not settings.llamacpp_model_path:
            raise ValueError("LLAMACPP_MODEL_PATH is required for LlamaCpp provider")

        return LlamaCpp(
            model_path=settings.llamacpp_model_path,
            n_ctx=settings.llamacpp_n_ctx,
            n_gpu_layers=settings.llamacpp_n_gpu_layers,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_embeddings():
    """Get embeddings model."""
    provider = settings.llm_provider.lower()

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=settings.openai_api_key)

    elif provider == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings

        return OllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )

    else:
        # Default to OpenAI embeddings
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=settings.openai_api_key)
