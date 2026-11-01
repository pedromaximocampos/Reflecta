"""OpenAI Responses transport; application validation remains provider independent."""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Literal, TypeVar

import httpx
from pydantic import BaseModel, Field, SecretStr
from src.modules.ai_processing.application.contextual_passage_selection import (
    ContextualPassageSelection,
    ContextualPassageSelectionRequest,
)
from src.modules.ai_processing.application.failure_reasons import FailureReason
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.modules.ai_processing.application.contracts import (
    Interpretation, InterpretationFailedError, InterpretationRequest,
    ProviderNotConfiguredError,
)


BACKEND_ROOT = Path(__file__).resolve().parents[4]
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
logger = logging.getLogger(__name__)


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_", env_file=(
            BACKEND_ROOT / f".env.{os.getenv('ENV', 'dev')}",
            BACKEND_ROOT / ".env.ai.local",
        ), extra="ignore",
    )
    api_key: SecretStr = SecretStr("")
    model: str = "gpt-6-luna"
    timeout_seconds: float = Field(default=60, gt=0)
    max_output_tokens: int = Field(default=12000, gt=0)
    provider_max_attempts: int = Field(default=3, ge=1, le=5)
    provider_retry_base_seconds: float = Field(default=1.0, gt=0, le=10)
    reasoning_effort: Literal["minimal", "low", "medium", "high", "none", "xhigh", "max"] | None = None


class OpenAIInterpreter:
    def __init__(self, settings: OpenAISettings, *, transport=None):
        self.settings = settings
        self.transport = transport
        self._client: httpx.AsyncClient | None = None
        self._scope_lock = asyncio.Lock()

    def _new_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.settings.timeout_seconds,
            transport=self.transport,
        )

    @asynccontextmanager
    async def request_scope(self) -> AsyncIterator[None]:
        """Reuse one verified connection pool for one complete AI workflow."""
        async with self._scope_lock:
            async with self._new_client() as client:
                self._client = client
                try:
                    yield
                finally:
                    self._client = None

    def ensure_available(self) -> None:
        if not self.settings.api_key.get_secret_value().strip() or not self.settings.model.strip():
            raise ProviderNotConfiguredError("Configure OPENAI_API_KEY and OPENAI_MODEL.")

    async def interpret(self, request: InterpretationRequest) -> dict:
        return await self._structured_response(
            instructions=request.instructions,
            input_data={
                "content_text": request.content_text,
                "context_tags": request.context_tags,
                "themes": [theme.model_dump() for theme in request.themes],
            },
            response_model=Interpretation,
            schema_name="journal_interpretation",
        )

    async def select_contextual_passages(
        self,
        request: ContextualPassageSelectionRequest,
    ) -> dict:
        return await self._structured_response(
            instructions=request.instructions,
            input_data=request.model_dump(
                mode="json",
                exclude={"instructions"},
            ),
            response_model=ContextualPassageSelection,
            schema_name="contextual_passage_selection",
        )

    async def respond(self, *, instructions, input_data, schema):
        return await self._structured_response(
            instructions=instructions,
            input_data=input_data,
            response_model=schema,
            schema_name="journal_interpretation",
        )

    async def _structured_response(
        self,
        *,
        instructions: str,
        input_data: dict[str, Any],
        response_model: type[ResponseModel],
        schema_name: str,
    ) -> dict:
        self.ensure_available()
        payload = {
            "model": self.settings.model,
            "instructions": instructions,
            "input": [{
                "role": "user",
                "content": json.dumps(input_data, ensure_ascii=False),
            }],
            "store": False,
            "max_output_tokens": self.settings.max_output_tokens,
            "text": {"format": {
                "type": "json_schema", "name": schema_name,
                "strict": True, "schema": response_model.model_json_schema(),
            }},
        }
        effort = self.settings.reasoning_effort
        if effort is None and self.settings.model.startswith("gpt-5-nano"):
            effort = "minimal"
        if effort is not None:
            payload["reasoning"] = {"effort": effort}
        try:
            response = await self._send(payload, operation=schema_name)
            response.raise_for_status()
            body = response.json()
            if body.get("status") != "completed":
                raise InterpretationFailedError(reason=FailureReason.INCOMPLETE)
            parts = []
            for item in body.get("output", []):
                if item.get("type") != "message":
                    continue
                for part in item.get("content", []):
                    if part.get("type") == "refusal":
                        raise InterpretationFailedError(reason=FailureReason.REFUSAL)
                    if part.get("type") == "output_text":
                        parts.append(part["text"])
            return response_model.model_validate_json("".join(parts)).model_dump()
        except InterpretationFailedError:
            raise
        except httpx.TimeoutException as error:
            logger.error(
                "OpenAI request timed out: operation=%s error_type=%s",
                schema_name,
                type(error).__name__,
            )
            raise InterpretationFailedError(reason=FailureReason.TIMEOUT) from None
        except httpx.TransportError as error:
            logger.error(
                "OpenAI transport failed: operation=%s error_type=%s cause_type=%s",
                schema_name,
                type(error).__name__,
                type(_root_cause(error)).__name__,
            )
            raise InterpretationFailedError(reason=FailureReason.NETWORK) from None
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            reason = {
                400: FailureReason.REQUEST, 401: FailureReason.AUTH,
                403: FailureReason.PERMISSION, 404: FailureReason.MODEL,
                429: FailureReason.RATE_LIMIT,
            }.get(status, FailureReason.UNAVAILABLE if status >= 500 else FailureReason.HTTP)
            if status == 429:
                try:
                    if error.response.json().get("error", {}).get("code") == "insufficient_quota":
                        reason = FailureReason.QUOTA
                except (ValueError, AttributeError, TypeError):
                    pass
            raise InterpretationFailedError(reason=reason) from None
        except Exception:
            raise InterpretationFailedError(reason=FailureReason.RESPONSE) from None

    async def _send(
        self,
        payload: dict[str, Any],
        *,
        operation: str,
    ) -> httpx.Response:
        if self._client is not None:
            return await self._post_with_retry(
                self._client,
                payload,
                operation=operation,
            )
        async with self._new_client() as client:
            return await self._post_with_retry(
                client,
                payload,
                operation=operation,
            )

    async def _post_with_retry(
        self,
        client: httpx.AsyncClient,
        payload: dict[str, Any],
        *,
        operation: str,
    ) -> httpx.Response:
        max_attempts = self.settings.provider_max_attempts
        for attempt in range(1, max_attempts + 1):
            try:
                return await client.post(
                    "https://api.openai.com/v1/responses",
                    json=payload,
                    headers={
                        "Authorization": "Bearer "
                        + self.settings.api_key.get_secret_value(),
                    },
                )
            except httpx.ConnectError as error:
                if attempt >= max_attempts:
                    raise
                delay_seconds = (
                    self.settings.provider_retry_base_seconds
                    * (2 ** (attempt - 1))
                )
                logger.warning(
                    "OpenAI connection retry scheduled: operation=%s "
                    "attempt=%s max_attempts=%s delay_seconds=%s "
                    "error_type=%s cause_type=%s",
                    operation,
                    attempt,
                    max_attempts,
                    delay_seconds,
                    type(error).__name__,
                    type(_root_cause(error)).__name__,
                )
                await asyncio.sleep(delay_seconds)
        raise RuntimeError("OpenAI connection retry loop ended unexpectedly.")


def _root_cause(error: BaseException) -> BaseException:
    cause = error
    visited: set[int] = set()
    while id(cause) not in visited:
        visited.add(id(cause))
        nested = cause.__cause__ or cause.__context__
        if nested is None:
            break
        cause = nested
    return cause
