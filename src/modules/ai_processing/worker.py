"""Durable PostgreSQL pending queue. Run with --once for one entry."""
import argparse
import asyncio
import logging
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from neo4j.exceptions import Neo4jError, DriverError

from src.modules.ai_processing.application.failure_reasons import FailureReason
from src.modules.ai_processing.application.contracts import InterpretationFailedError, InvalidJournalInputError
from src.modules.journal.public.analysis import AnalysisFailure

from src.modules.ai_processing.application.contracts import ProviderNotConfiguredError, InvalidInterpretationError
from src.modules.journal.public.analysis import AnalysisConflictError

logger = logging.getLogger(__name__)
LOCK_ID = 190024


@asynccontextmanager
async def provider_request_scope(case):
    """Keep each distinct provider pool open for the complete analysis."""
    async with AsyncExitStack() as stack:
        providers = (
            getattr(case, "interpreter", None),
            getattr(case, "passage_selector", None),
        )
        entered: set[int] = set()
        for provider in providers:
            request_scope = getattr(provider, "request_scope", None)
            if provider is None or request_scope is None or id(provider) in entered:
                continue
            entered.add(id(provider))
            await stack.enter_async_context(request_scope())
        yield


def failure_reason(error):
    if isinstance(error, InterpretationFailedError):
        return error.reason
    if isinstance(error, InvalidJournalInputError):
        return FailureReason.INPUT
    if isinstance(error, SQLAlchemyError):
        return FailureReason.DATABASE
    if isinstance(error, (Neo4jError, DriverError)):
        return FailureReason.CATALOG
    return FailureReason.UNEXPECTED


async def process_one(gateway, interpreter, *, entry_id=None, case_factory=None):
    snapshot = await gateway.next_pending(entry_id)
    if snapshot is None:
        return False
    attempt = 0
    try:
        if getattr(snapshot, "processing_settings", None) is not None:
            if case_factory is None:
                raise ProviderNotConfiguredError("Per-attempt settings require a case factory.")
            interpreter = case_factory(processing_settings=snapshot.processing_settings)
        async with provider_request_scope(interpreter):
            # One bounded retry for an invalid AI result; never loop indefinitely.
            # Failed validations do not save data. Connection establishment has its
            # own bounded retry inside the provider adapter.
            for attempt in range(2):
                try:
                    analysis_id = await interpreter.execute(snapshot.entry_id, snapshot.user_id)
                    break
                except InvalidInterpretationError:
                    if attempt == 1:
                        raise
                    logger.warning("Invalid analysis result; retrying entry=%s attempt=2/2", snapshot.entry_id)
    except ProviderNotConfiguredError:
        raise
    except AnalysisConflictError:
        logger.info("Entry changed or already analyzed: %s", snapshot.entry_id)
    except Exception as error:
        reason = failure_reason(error)
        await gateway.mark_failed(
            snapshot, now=datetime.now(timezone.utc),
            failure=AnalysisFailure(reason.value, reason.message, attempt + 1),
        )
        logger.error("Analysis failed entry=%s code=%s attempts=%s", snapshot.entry_id, reason.value, attempt + 1)
    else:
        logger.info("Analysis saved entry=%s analysis=%s", snapshot.entry_id, analysis_id)
    return True


async def run(args):
    from src.modules.ai_processing.bootstrap.use_cases import get_interpret_entry
    from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider as db
    from src.shared.infrastructure.persistence.neo4j.provider import reflecta_neo4j_provider
    case = get_interpret_entry()
    case.interpreter.ensure_available()
    gateway = JournalAnalysisGateway(db)
    try:
        while True:
            # Session-scoped advisory lock survives commits, with no transaction
            # held during the external request. Always released before pooling.
            async with db.engine.connect() as connection:
                connection = await connection.execution_options(isolation_level="AUTOCOMMIT")
                acquired = await connection.scalar(text("SELECT pg_try_advisory_lock(:id)"), {"id": LOCK_ID})
                try:
                    if acquired:
                        await process_one(gateway, case, entry_id=args.entry_id, case_factory=get_interpret_entry)
                finally:
                    if acquired:
                        await connection.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": LOCK_ID})
            if args.once:
                return
            await asyncio.sleep(args.poll_seconds)
    finally:
        await db.dispose()
        await reflecta_neo4j_provider.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--entry-id", help="Only process this pending entry")
    parser.add_argument("--poll-seconds", type=float, default=5)
    args = parser.parse_args()
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be positive")
    logging.basicConfig(level=logging.INFO)
    # Existing settings bootstrap may reset log levels.
    logger.setLevel(logging.INFO)
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
