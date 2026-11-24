from datetime import datetime

from sqlalchemy import select

from src.modules.sharing.infrastructure.persistence.postgresql.models.context_share_model import (
    ContextShareModel,
)
from src.modules.sharing.infrastructure.persistence.postgresql.models.professional_activity_model import (
    ProfessionalActivityModel,
)
from src.modules.sharing.public.data_export import (
    ISharingDataExportFacade,
    SharingDataExport,
)


def _iso(value) -> str | None:
    return value.isoformat() if value is not None else None


class PostgresSharingDataExportFacade(ISharingDataExportFacade):
    def __init__(self, db) -> None:
        self._db = db

    async def export_sharing(
        self,
        user_id: str,
        *,
        generated_at: datetime,
    ) -> SharingDataExport:
        async with self._db.session() as session:
            shares = (
                await session.execute(
                    select(ContextShareModel)
                    .where(ContextShareModel.user_id == user_id)
                    .order_by(ContextShareModel.created_at, ContextShareModel.id)
                )
            ).scalars().all()
            activities = (
                await session.execute(
                    select(ProfessionalActivityModel)
                    .where(ProfessionalActivityModel.user_id == user_id)
                    .order_by(
                        ProfessionalActivityModel.created_at,
                        ProfessionalActivityModel.id,
                    )
                )
            ).scalars().all()

        exported_shares = tuple(
            {
                "id": share.id,
                "analysis_id": share.analysis_id,
                "status": (
                    "revoked"
                    if share.revoked_at is not None
                    else "expired"
                    if share.expires_at <= generated_at
                    else "active"
                ),
                "shared_content_snapshot": share.snapshot,
                "created_at": _iso(share.created_at),
                "expires_at": _iso(share.expires_at),
                "revoked_at": _iso(share.revoked_at),
            }
            for share in shares
        )
        exported_activities = tuple(
            {
                "id": activity.id,
                "share_id": activity.share_id,
                "kind": activity.kind,
                "title": activity.title,
                "description": activity.description,
                "due_date": _iso(activity.due_date),
                "status": activity.status,
                "created_at": _iso(activity.created_at),
                "completed_at": _iso(activity.completed_at),
            }
            for activity in activities
        )
        return SharingDataExport(
            shares=exported_shares,
            professional_activities=exported_activities,
        )
