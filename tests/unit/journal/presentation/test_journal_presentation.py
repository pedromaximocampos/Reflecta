from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.modules.journal.presentation.controllers.get_journal_entry_controller import (
    GetJournalEntryController,
)
from src.modules.journal.presentation.controllers.update_journal_entry_controller import (
    UpdateJournalEntryController,
)
from src.modules.journal.presentation.validators.journal_entry import (
    CreateJournalEntryValidator,
    UpdateJournalEntryValidator,
)
from src.shared.presentation.http_types import HttpRequest


USER_ID = "01USER0000000000000000000"
ENTRY_ID = "01JOURNAL00000000000000000"


class Output:
    def to_dict(self) -> dict:
        return {"id": ENTRY_ID}


def make_request(*, body=None) -> HttpRequest:
    return HttpRequest(
        method="PATCH",
        url=f"http://test/journal/entries/{ENTRY_ID}",
        body=body,
        path_params={"journal_entry_id": ENTRY_ID},
        authenticated_user_id=USER_ID,
    )


def test_create_validator_normalizes_content_and_serializes_context_tags() -> None:
    validator = CreateJournalEntryValidator.model_validate(
        {
            "title": " Meu dia ",
            "content_text": " Uma reflexão. ",
            "context_tags": {
                "people": [{"label": " Família ", "source": "user"}]
            },
        }
    )

    payload = validator.model_dump(mode="json")
    assert payload["title"] == "Meu dia"
    assert payload["content_text"] == "Uma reflexão."
    assert payload["context_tags"]["people"][0]["label"] == "Família"


@pytest.mark.parametrize("content", ["", "   "])
def test_create_validator_rejects_blank_content(content: str) -> None:
    with pytest.raises(ValidationError):
        CreateJournalEntryValidator(content_text=content)


def test_update_validator_rejects_empty_payload_and_null_content() -> None:
    with pytest.raises(ValidationError):
        UpdateJournalEntryValidator.model_validate({})
    with pytest.raises(ValidationError):
        UpdateJournalEntryValidator.model_validate({"content_text": None})


def test_update_validator_allows_clearing_optional_title_and_tags() -> None:
    validator = UpdateJournalEntryValidator.model_validate(
        {"title": None, "context_tags": None}
    )

    assert validator.model_dump(exclude_unset=True) == {
        "title": None,
        "context_tags": None,
    }


@pytest.mark.asyncio
async def test_get_controller_uses_authenticated_user_id() -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = Output()
    controller = GetJournalEntryController(use_case)

    response = await controller.handle_request(make_request())

    journal_input = use_case.execute.await_args.args[0]
    assert journal_input.user_id.value == USER_ID
    assert journal_input.journal_entry_id.value == ENTRY_ID
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_controller_preserves_explicit_fields() -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = Output()
    controller = UpdateJournalEntryController(use_case)

    await controller.handle_request(
        make_request(body={"title": None, "context_tags": None})
    )

    journal_input = use_case.execute.await_args.args[0]
    assert journal_input.user_id.value == USER_ID
    assert journal_input.fields_to_update == frozenset({"title", "context_tags"})
