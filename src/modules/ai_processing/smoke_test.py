"""Run with python -m src.modules.ai_processing.smoke_test (one paid request)."""
import asyncio
import json

import httpx

from src.modules.ai_processing.application.contracts import InterpretationRequest
from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAIInterpreter, OpenAISettings


class DiagnosticTransport(httpx.AsyncBaseTransport):
    def __init__(self):
        self.inner = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request):
        try:
            response = await self.inner.handle_async_request(request)
        except httpx.TransportError as error:
            print("Network error:", type(error).__name__)
            raise
        await response.aread()
        print("HTTP status:", response.status_code)
        try:
            body = response.json()
            error = body.get("error") or {}
            # No raw error messages: they may contain credentials or input data.
            safe_codes = {"insufficient_quota", "invalid_api_key", "model_not_found",
                          "rate_limit_exceeded", "invalid_json_schema"}
            code = error.get("code")
            if code in safe_codes:
                print("API error code:", code)
            if body.get("status") == "incomplete":
                print("Incomplete response: check the output token budget.")
            if body.get("usage"):
                print("Usage:", json.dumps(body["usage"]))
        except (ValueError, TypeError):
            pass
        return response

    async def aclose(self):
        await self.inner.aclose()


async def main():
    settings = OpenAISettings()
    print("Model:", settings.model)
    try:
        result = await OpenAIInterpreter(settings, transport=DiagnosticTransport()).interpret(
            InterpretationRequest(
                content_text="Hoje terminei uma tarefa difícil. Fiquei cansado, mas feliz.",
                context_tags=None, themes=(),
            ),
        )
    except Exception as error:
        print("Failure:", type(error).__name__)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
