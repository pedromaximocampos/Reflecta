from typing import Protocol

from .types import EntityT, ModelT


class IMapper(Protocol[ModelT, EntityT]):
    def to_entity(self, model: ModelT) -> EntityT:
        ...

    def to_model(self, entity: EntityT) -> ModelT:
        ...