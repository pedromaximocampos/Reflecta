from typing import Mapping, Optional
from src.application.ports.messaging.ievent_publisher import IEventPublisherWorker

class EventRouter:
    def __init__(self, routes: Mapping[str, IEventPublisherWorker], *, default: Optional[IEventPublisherWorker] = None) -> None:
        self.__routes = dict(routes)
        self.__default = default


    def resolve(self, event_type: str) -> IEventPublisherWorker:

        domain, _, _ =  event_type.partition('.')

        pub = self.__routes.get(domain, None)
        if pub:
            return pub

        if self.__default:
            return self.__default

        raise KeyError(f"No publisher configured for domain '{domain}' (event='{event_type}')")


