from typing import Protocol


class IEventConsumerWorker(Protocol):
    async def start(self) -> None: ...

    async def handle_message(self, payload: dict): ...