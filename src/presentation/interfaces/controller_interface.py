from abc import ABC, abstractmethod
from src.presentation.http_types.http_request import HttpRequest
from src.presentation.http_types.http_response import HttpResponse


class IControllerInterface(ABC):

    @abstractmethod
    async def handle_request(self, request: HttpRequest) -> HttpResponse: pass