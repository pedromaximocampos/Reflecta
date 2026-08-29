from typing import Protocol


class IOutboxDispatcherWorker(Protocol):

    async def start(self)-> None: ...