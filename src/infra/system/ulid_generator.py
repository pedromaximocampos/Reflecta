import uuid

from src.domain.ports.system.ulid_generator import IULIDGenerator
import ulid


class UlidGenerator(IULIDGenerator):

    def generate_ulid(self) -> str:
        return str(ulid.new())
