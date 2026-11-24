from sqlalchemy import func, select

from src.modules.ai_processing.application.contextual_analysis import ContextResult
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import (
    UserModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.journal_share_snapshot import (
    JournalShareSnapshotBuilder,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.context_analysis_model import (
    ContextAnalysisModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.public.context_analysis import ContextPeriod
from src.modules.journal.public.context_share import (
    ContextAnalysisDescriptor,
    IJournalSharingFacade,
    JournalShareSourceIneligible,
    JournalShareSourceUnavailable,
    ShareableContextAnalysis,
)


class PostgresJournalSharingFacade(IJournalSharingFacade):
    """Public Journal capability consumed by the Sharing module."""

    def __init__(self, db, snapshot_builder=None) -> None:
        self._db = db
        self._snapshot_builder = snapshot_builder or JournalShareSnapshotBuilder()

    @staticmethod
    def _owned_query(analysis_id: str, user_id: str):
        return (
            select(ContextAnalysisModel)
            .join(UserModel, UserModel.id == ContextAnalysisModel.user_id)
            .where(
                ContextAnalysisModel.id == analysis_id,
                ContextAnalysisModel.user_id == user_id,
                UserModel.deleted_at.is_(None),
            )
        )

    @staticmethod
    async def _sources_available(session, analysis: ContextAnalysisModel) -> bool:
        if not analysis.entry_ids:
            return False
        count = await session.scalar(
            select(func.count())
            .select_from(JournalEntryModel)
            .where(
                JournalEntryModel.id.in_(analysis.entry_ids),
                JournalEntryModel.user_id == analysis.user_id,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.status != "deleted",
            )
        )
        return count == len(set(analysis.entry_ids))

    @staticmethod
    def _descriptor(analysis: ContextAnalysisModel) -> ContextAnalysisDescriptor:
        period = None
        if analysis.period_start and analysis.period_end:
            period = ContextPeriod(
                start_date=analysis.period_start,
                end_date=analysis.period_end,
            ).describe()
        return ContextAnalysisDescriptor(
            analysis_id=analysis.id,
            created_at=analysis.created_at,
            period=period,
            entry_count=len(analysis.entry_ids),
            summary=(analysis.result or {}).get("summary"),
        )

    async def prepare_share(
        self,
        analysis_id: str,
        user_id: str,
        *,
        include_journals: bool,
    ) -> ShareableContextAnalysis:
        async with self._db.session() as session:
            analysis = await session.scalar(self._owned_query(analysis_id, user_id))
            if analysis is None:
                raise JournalShareSourceUnavailable()
            if (
                not analysis.period_start
                or not analysis.period_end
                or len(analysis.entry_ids) < 5
                or not await self._sources_available(session, analysis)
            ):
                raise JournalShareSourceIneligible()

            entries = []
            if include_journals:
                entries = await self._snapshot_builder.build(session, analysis, user_id)
                if entries is None:
                    raise JournalShareSourceIneligible()

            period = ContextPeriod(
                start_date=analysis.period_start,
                end_date=analysis.period_end,
            )
            return ShareableContextAnalysis(
                period=period.describe(),
                created_at=analysis.created_at,
                entry_count=len(analysis.entry_ids),
                result=ContextResult.model_validate(analysis.result).model_dump(),
                entries=entries,
            )

    async def ensure_available(self, analysis_id: str, user_id: str) -> None:
        async with self._db.session() as session:
            analysis = await session.scalar(self._owned_query(analysis_id, user_id))
            if analysis is None or not await self._sources_available(session, analysis):
                raise JournalShareSourceUnavailable()

    async def describe_owned(
        self,
        analysis_id: str,
        user_id: str,
    ) -> ContextAnalysisDescriptor:
        async with self._db.session() as session:
            analysis = await session.scalar(self._owned_query(analysis_id, user_id))
            if analysis is None:
                raise JournalShareSourceUnavailable()
            return self._descriptor(analysis)

    async def describe_owned_many(
        self,
        analysis_ids: tuple[str, ...],
        user_id: str,
    ) -> dict[str, ContextAnalysisDescriptor]:
        if not analysis_ids:
            return {}
        async with self._db.session() as session:
            analyses = (
                await session.execute(
                    select(ContextAnalysisModel)
                    .join(UserModel, UserModel.id == ContextAnalysisModel.user_id)
                    .where(
                        ContextAnalysisModel.id.in_(analysis_ids),
                        ContextAnalysisModel.user_id == user_id,
                        UserModel.deleted_at.is_(None),
                    )
                )
            ).scalars().all()
            return {
                analysis.id: self._descriptor(analysis)
                for analysis in analyses
            }
