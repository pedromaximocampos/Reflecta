from typing import Mapping, Optional
from src.modules.internal_events.application.ports.messaging.ievent_publisher import IEventPublisher
from src.modules.internal_events.domain.value_objects.event_type import EventType


class EventRouter:
    def __init__(self, routes: Mapping[str, IEventPublisher], *, default: Optional[IEventPublisher] = None) -> None:
        self.__routes = dict(routes)
        self.__default = default

    @property
    def publishers(self) -> tuple[IEventPublisher, ...]:
        publishers = list(self.__routes.values())
        if self.__default is not None:
            publishers.append(self.__default)

        return tuple({id(publisher): publisher for publisher in publishers}.values())

    async def start(self) -> None:
        for publisher in self.publishers:
            await publisher.start()

    async def stop(self) -> None:
        for publisher in reversed(self.publishers):
            await publisher.stop()

    def resolve_publisher(self, event_type: EventType) -> IEventPublisher:
        pub = self.__routes.get(event_type.value)
        if pub is None:
            pub = self.__routes.get(event_type.domain)
        if pub:
            return pub

        if self.__default:
            return self.__default

        raise KeyError(f"No publisher configured for domain '{event_type.domain}' (event='{event_type}')")


