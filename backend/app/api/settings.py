"""Settings API routes."""

from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/integrations")
async def get_integration_status() -> Dict[str, Any]:
    """Get status of all integrations."""
    return {
        "calendar": {
            "enabled": bool(settings.google_credentials_path or settings.outlook_client_id),
            "provider": "google" if settings.google_credentials_path else "outlook" if settings.outlook_client_id else None,
            "status": "configured" if settings.google_credentials_path else "not_configured"
        },
        "email": {
            "enabled": bool(settings.imap_host),
            "provider": "imap" if settings.imap_host else None,
            "status": "configured" if settings.imap_host else "not_configured"
        },
        "crm": {
            "enabled": bool(settings.crm_api_key),
            "provider": settings.crm_provider,
            "status": "configured" if settings.crm_api_key else "not_configured"
        },
        "llm": {
            "provider": settings.llm_provider,
            "model": _get_current_model(),
            "status": "configured"
        }
    }


@router.get("/llm")
async def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration."""
    return {
        "provider": settings.llm_provider,
        "model": _get_current_model(),
        "available_providers": ["openai", "anthropic", "ollama", "llamacpp"]
    }


def _get_current_model() -> str:
    """Get currently configured model name."""
    provider = settings.llm_provider.lower()
    if provider == "openai":
        return settings.openai_model
    elif provider == "anthropic":
        return settings.anthropic_model
    elif provider == "ollama":
        return settings.ollama_model
    elif provider == "llamacpp":
        return settings.llamacpp_model_path or "not_configured"
    return "unknown"
