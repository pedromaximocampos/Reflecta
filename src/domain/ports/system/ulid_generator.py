from abc import ABC, abstractmethod



class IULIDGenerator(ABC):

    @abstractmethod
    def generate_ulid(self) -> str: pass