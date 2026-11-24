from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus
from src.modules.sharing.infrastructure.persistence.postgresql.models import (
    ProfessionalActivityModel,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class ProfessionalActivityMapper(
    IMapper[ProfessionalActivityModel, ProfessionalActivity]
):
    def to_entity(self, model: ProfessionalActivityModel) -> ProfessionalActivity:
        return ProfessionalActivity(
            id=model.id,
            share_id=model.share_id,
            user_id=model.user_id,
            kind=ActivityKind(model.kind),
            title=model.title,
            description=model.description,
            due_date=model.due_date,
            status=ActivityStatus(model.status),
            created_at=model.created_at,
            completed_at=model.completed_at,
        )

    def to_model(self, entity: ProfessionalActivity) -> ProfessionalActivityModel:
        return ProfessionalActivityModel(
            id=entity.id,
            share_id=entity.share_id,
            user_id=entity.user_id,
            kind=entity.kind.value,
            title=entity.title,
            description=entity.description,
            due_date=entity.due_date,
            status=entity.status.value,
            created_at=entity.created_at,
            completed_at=entity.completed_at,
        )

