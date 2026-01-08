from typing import Mapping, Optional
from src.application.ports.messaging.ievent_publisher import IEventPublisher

class EventRouter:
    def __init__(self, routes: Mapping[str, IEventPublisher], *, default: Optional[IEventPublisher] = None) -> None:
        self.__routes = dict(routes)
        self.__default = default


    def resolve(self, event_type: str) -> IEventPublisher:

        domain, _, _ =  event_type.partition('.')

        pub = self.__routes.get(domain, None)
        if pub:
            return pub

        if self.__default:
            return self.__default

        raise KeyError(f"No publisher configured for domain '{domain}' (event='{event_type}')")


