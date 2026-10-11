"""OpenAI Responses transport; application validation remains provider independent."""
import json
import os
from pathlib import Path
from typing import Literal

import httpx
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.modules.ai_processing.application.contracts import (
    Interpretation, InterpretationFailedError, InterpretationRequest,
    ProviderNotConfiguredError,
)


BACKEND_ROOT = Path(__file__).resolve().parents[4]


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_", env_file=(
            BACKEND_ROOT / f".env.{os.getenv('ENV', 'dev')}",
            BACKEND_ROOT / ".env.ai.local",
        ), extra="ignore",
    )
    api_key: SecretStr = SecretStr("")
    model: str = ""
    timeout_seconds: float = Field(default=30, gt=0)
    max_output_tokens: int = Field(default=2000, gt=0)
    provider_max_attempts: int = Field(default=3, ge=1, le=5)
    provider_retry_base_seconds: float = Field(default=1.0, gt=0, le=10)
    reasoning_effort: Literal["minimal", "low", "medium", "high", "none"] | None = None


class OpenAIInterpreter:
    def __init__(self, settings: OpenAISettings, *, transport=None):
        self.settings = settings
        self.transport = transport

    def ensure_available(self) -> None:
        if not self.settings.api_key.get_secret_value().strip() or not self.settings.model.strip():
            raise ProviderNotConfiguredError("Configure OPENAI_API_KEY and OPENAI_MODEL.")

    async def interpret(self, request: InterpretationRequest) -> dict:
        self.ensure_available()
        payload = {
            "model": self.settings.model,
            "instructions": request.instructions,
            "input": [{"role": "user", "content": json.dumps({
                "content_text": request.content_text,
                "context_tags": request.context_tags,
                "themes": [theme.model_dump() for theme in request.themes],
            }, ensure_ascii=False)}],
            "store": False,
            "max_output_tokens": self.settings.max_output_tokens,
            "text": {"format": {
                "type": "json_schema", "name": "journal_interpretation",
                "strict": True, "schema": Interpretation.model_json_schema(),
            }},
        }
        effort = self.settings.reasoning_effort
        if effort is None and self.settings.model.startswith("gpt-5-nano"):
            effort = "minimal"
        if effort is not None:
            payload["reasoning"] = {"effort": effort}
        try:
            # No automatic retries: orchestration and retry policy belong to UC24/UC25.
            async with httpx.AsyncClient(
                timeout=self.settings.timeout_seconds, transport=self.transport,
            ) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses", json=payload,
                    headers={"Authorization": "Bearer " + self.settings.api_key.get_secret_value()},
                )
                response.raise_for_status()
                body = response.json()
            if body.get("status") != "completed":
                raise ValueError("Incomplete response")
            parts = []
            for item in body.get("output", []):
                if item.get("type") != "message":
                    continue
                for part in item.get("content", []):
                    if part.get("type") == "refusal":
                        raise ValueError("Refused response")
                    if part.get("type") == "output_text":
                        parts.append(part["text"])
            return Interpretation.model_validate_json("".join(parts)).model_dump()
        except Exception:
            raise InterpretationFailedError("Text interpretation failed.") from None
