import asyncio
from typing import Final

from src.application.ports.messaging.ioutbox_dispatcher_worker import IOutboxDispatcherWorker
from src.application.ports.strategies.ibackoff_strategies import IBackoffStrategy
from src.domain.ports.system.iclock import IClock
from src.domain.ports.units_of_work.ioutbox_unit_of_work import IOutboxUnitOfWork
from src.infra.messaging.routing.event_router import EventRouter


class BaseSqsPublisher(IOutboxDispatcherWorker):

    __BATCH_LIMIT: Final[int]
    __ATTEMPTS_LIMIT: Final[int]

    def __init__(self, event_router: EventRouter, uow: IOutboxUnitOfWork, batch_limit: int, system_clock: IClock, attempts_limit: int,
                 backoff_strategy: IBackoffStrategy) -> None:
        self.__event_router = event_router
        self.__uow = uow
        self.__BATCH_LIMIT = batch_limit
        self.__ATTEMPTS_LIMIT = attempts_limit
        self.__clock = system_clock
        self.__backoff_strategy = backoff_strategy

    async def start(self) -> None:
        print(f"running {self.__class__.__name__} worker... OutboxDispatcherWorker")
        while True:

            async with self.__uow as uow:
                events =  await uow.outbox_repository.claim_pending(self.__BATCH_LIMIT, self.__ATTEMPTS_LIMIT)
                await uow.commit()

            if not events:
                await asyncio.sleep(1)
                continue

            for event in events:
                try:
                    publisher =  self.__event_router.resolve_publisher(event.event_type)

                    await publisher.publish(event)
                    async with self.__uow as uow:

                        event.sent_at = self.__clock.now()
                        await uow.outbox_repository.mark_sent(event)
                        await uow.commit()

                except Exception as e:
                    async with self.__uow as uow:
                        event.last_error = str(e)
                        event.failed_at = self.__clock.now()
                        event.next_attempt_at  = self.__clock.now() + self.__backoff_strategy.next_delay_in_seconds(event.attempts)
                        await uow.outbox_repository.mark_failed(event)
                        await uow.commit()