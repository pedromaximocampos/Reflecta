from src.modules.ai_processing.application.contracts import (
    InterpretationRequest, ProviderNotConfiguredError,
)


class UnconfiguredInterpreter:
    def ensure_available(self) -> None:
        raise ProviderNotConfiguredError("AI provider is not configured.")

    async def interpret(self, request: InterpretationRequest) -> dict:
        self.ensure_available()
        raise AssertionError("Unreachable")
