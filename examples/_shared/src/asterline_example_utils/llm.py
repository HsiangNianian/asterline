from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from asterline import LLMClient, LLMConfig
from asterline import AgentError
from asterline.agent import clip_text as _clip_text
from asterline.agent import format_transcript as _format_transcript
from asterline.config import load_env_file
from pydantic import BaseModel

load_env_file(Path(__file__).resolve().parents[2] / ".env")

DEFAULT_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "kimi-k2.5")
LLMSettings = LLMConfig
LLMError = AgentError
clip_text = _clip_text
format_transcript = _format_transcript


def resolve_llm_settings(
    config_obj: Any | None,
    *,
    default_temperature: float = 0.7,
    default_max_tokens: int = 800,
) -> LLMSettings:
    raw = getattr(config_obj, "llm", None) if config_obj is not None else None
    if isinstance(raw, BaseModel):
        payload = raw.model_dump(mode="python")
    elif isinstance(raw, dict):
        payload = dict(raw)
    elif isinstance(raw, LLMConfig):
        return raw
    else:
        payload = {}
    payload.setdefault("base_url", DEFAULT_BASE_URL)
    payload.setdefault("model", DEFAULT_MODEL)
    payload.setdefault("temperature", default_temperature)
    payload.setdefault("max_tokens", default_max_tokens)
    return LLMConfig.from_mapping(payload)


async def chat_text(
    settings: LLMSettings,
    messages: list[dict[str, str]],
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    return await LLMClient(settings).chat_text(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


async def chat_json(
    settings: LLMSettings,
    messages: list[dict[str, str]],
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any] | list[Any]:
    return await LLMClient(settings).chat_json(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
