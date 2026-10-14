import asyncio
import logging

from src.modules.ai_processing.application.ports.inbox import IWorkIngestionInbox


_LOGGER = logging.getLogger(__name__)


class InboxClaimHeartbeat:
    def __init__(
        self,
        *,
        inbox: IWorkIngestionInbox,
        event_id: str,
        expected_attempt: int,
        lease_seconds: int,
        interval_seconds: int,
    ) -> None:
        self._inbox = inbox
        self._event_id = event_id
        self._expected_attempt = expected_attempt
        self._lease_seconds = lease_seconds
        self._interval_seconds = interval_seconds
        self._task: asyncio.Task[None] | None = None
        self._failure: Exception | None = None

    async def __aenter__(self) -> "InboxClaimHeartbeat":
        self._task = asyncio.create_task(self._run())
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    def raise_if_failed(self) -> None:
        if self._failure is not None:
            raise RuntimeError("Inbox claim heartbeat failed.") from self._failure

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            try:
                await self._inbox.renew(
                    self._event_id,
                    expected_attempt=self._expected_attempt,
                    lease_seconds=self._lease_seconds,
                )
            except Exception as error:
                self._failure = error
                _LOGGER.exception(
                    "Inbox heartbeat failed: event_id=%s attempt=%s",
                    self._event_id,
                    self._expected_attempt,
                )
                return
