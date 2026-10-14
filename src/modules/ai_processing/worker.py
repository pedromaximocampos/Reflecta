"""Durable PostgreSQL pending queue. Run with --once for one entry."""
import argparse
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import text

from src.modules.ai_processing.application.contracts import ProviderNotConfiguredError
from src.modules.journal.public.analysis import AnalysisConflictError

logger = logging.getLogger(__name__)
LOCK_ID = 190024


async def process_one(gateway, interpreter, *, entry_id=None):
    snapshot = await gateway.next_pending(entry_id)
    if snapshot is None:
        return False
    try:
        analysis_id = await interpreter.execute(snapshot.entry_id, snapshot.user_id)
    except ProviderNotConfiguredError:
        raise
    except AnalysisConflictError:
        logger.info("Entry changed or already analyzed: %s", snapshot.entry_id)
    except Exception as error:
        await gateway.mark_failed(snapshot, now=datetime.now(timezone.utc))
        logger.error("Analysis failed entry=%s error=%s", snapshot.entry_id, type(error).__name__)
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
                        await process_one(gateway, case, entry_id=args.entry_id)
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
