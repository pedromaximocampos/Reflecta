"""Create a fictitious entry and run the real worker for an existing user."""
import argparse
import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace

from sqlalchemy import select


async def main(user_id):
    from src.modules.auth.public.user_id import UserId
    from src.modules.journal.application.use_cases.create_entry.dto import CreateJournalEntryDTO
    from src.modules.journal.bootstrap.use_cases import get_create_journal_entry_use_case
    from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
    from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
    from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
    from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAISettings, OpenAIInterpreter
    from src.modules.ai_processing.worker import run
    from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider as db

    OpenAIInterpreter(OpenAISettings()).ensure_available()
    try:
        output = await get_create_journal_entry_use_case().execute(CreateJournalEntryDTO(
            user_id=UserId(user_id), title="Teste da análise por IA",
            content_text="Hoje terminei uma tarefa difícil no trabalho. Fiquei cansado, mas feliz com o resultado.",
        ))
        entry_id = output.to_dict()["id"]
        print("Created entry:", entry_id)
        await JournalAnalysisGateway(db).submit(entry_id, user_id, now=datetime.now(timezone.utc))
        await run(SimpleNamespace(once=True, entry_id=entry_id, poll_seconds=5))
        async with db.session() as session:
            status = await session.scalar(select(JournalEntryModel.status).where(JournalEntryModel.id == entry_id))
            result = (await session.execute(select(AnalysisModel).where(
                AnalysisModel.journal_entry_id == entry_id,
                AnalysisModel.status == "completed",
            ))).scalar_one_or_none()
            print("Entry status:", status)
            if result is None:
                print("No completed analysis saved. Check worker logs.")
                return 1
            print(json.dumps({"analysis_id": result.id, "summary": result.summary,
                              "main_message": result.main_message, "metadata": result.content_meta},
                             ensure_ascii=False, indent=2))
        return 0
    finally:
        await db.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", required=True, help="Existing user's ULID; creates one real entry and one paid request")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.user_id)))
