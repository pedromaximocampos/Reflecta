import asyncio
from typing import Final

from src.application.ports.messaging.ioutbox_dispatcher_worker import IOutboxDispatcherWorker
from src.domain.ports.system.iclock import IClock
from src.domain.ports.units_of_work.ioutbox_unit_of_work import IOutboxUnitOfWork
from src.infra.messaging.routing.event_router import EventRouter


class BaseSqsPublisher(IOutboxDispatcherWorker):

    __BATCH_LIMIT: Final[int]

    def __init__(self, event_router: EventRouter, uow: IOutboxUnitOfWork, batch_limit: int, system_clock: IClock) -> None:
        self.__event_router = event_router
        self.__uow = uow
        self.__BATCH_LIMIT = batch_limit
        self.__clock = system_clock

    async def start(self) -> None:

        while True:
            async with self.__uow as uow:
                events =  await uow.outbox_repository.list_pending(self.__BATCH_LIMIT)

            if not events:
                await asyncio.sleep(1)
                continue

            for event in events:
                try:
                    publisher =  self.__event_router.resolve_publisher(event.event_type)
                    async with self.__uow as uow:
                        await publisher.publish(event)
                        event.sent_at = self.__clock.now()
                        await uow.outbox_repository.mark_sent(event)

                except Exception as e:
                    async with self.__uow as uow:
                        event.last_error = str(e)
                        await uow.outbox_repository.mark_failed(event)