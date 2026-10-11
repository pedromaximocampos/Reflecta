import pytest

from src.modules.catalog.presentation.controllers.passage_controller import (
    CreatePassageController,
    UpdatePassageController,
)
from src.shared.presentation.http_types import HttpRequest


class _Result:
    def to_dict(self) -> dict:
        return {"id": "passage-id"}


class _UseCaseSpy:
    def __init__(self) -> None:
        self.input = None

    async def execute(self, input_dto):
        self.input = input_dto
        return _Result()


@pytest.mark.asyncio
async def test_create_controller_maps_only_create_fields() -> None:
    use_case = _UseCaseSpy()
    controller = CreatePassageController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="POST",
            url="/catalog/passages",
            body={
                "work_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "locator": "cap. 1",
                "short_text": "Uma passagem suficientemente longa para o catálogo.",
                "paraphrase": "Paráfrase.",
                "interpretation_note": "Nota.",
                "priority": 1,
                "themes": [
                    {
                        "theme_id": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
                        "confidence": 1.0,
                    }
                ],
                "start_page": 1,
                "end_page": 1,
            },
        )
    )

    assert response.status_code == 201
    assert use_case.input.start_page == 1
    assert use_case.input.end_page == 1


@pytest.mark.asyncio
async def test_update_controller_marks_explicit_null_page_range_as_provided() -> None:
    use_case = _UseCaseSpy()
    controller = UpdatePassageController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="PATCH",
            url="/catalog/passages/passage-id",
            body={"start_page": None, "end_page": None},
            path_params={"passage_id": "01ARZ3NDEKTSV4RRFFQ69G5FAX"},
        )
    )

    assert response.status_code == 200
    assert use_case.input.update_page_range is True
    assert use_case.input.start_page is None
    assert use_case.input.end_page is None
