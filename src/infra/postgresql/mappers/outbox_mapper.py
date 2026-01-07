from src.domain.entities.outbox_event import OutboxEvent
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.infra.postgresql.models.outbox_model import OutboxModel


class OutboxMapper(IMapper[OutboxModel, OutboxEvent]):

    def to_entity(self, model: OutboxModel) -> OutboxEvent:


        ...


    def to_model(self, entity: OutboxEvent) -> OutboxModel:
        ...