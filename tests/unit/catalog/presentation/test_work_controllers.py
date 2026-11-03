import pytest

from src.modules.catalog.presentation.controllers.get_works_controller import (
    GetAllWorksController,
    GetWorkByIdController,
)
from src.modules.catalog.presentation.controllers.update_work_cover_controller import (
    RemoveWorkCoverController,
    ReplaceWorkCoverController,
)
from src.shared.presentation.http_types import HttpRequest


class ResultStub:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def to_dict(self) -> dict:
        return self.payload


class UseCaseSpy:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.work_id = None

    async def execute(self, work_id=None):
        self.work_id = work_id
        return ResultStub(self.payload)


@pytest.mark.asyncio
async def test_get_work_controller_maps_path_id() -> None:
    work_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    use_case = UseCaseSpy({"id": work_id})
    controller = GetWorkByIdController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="GET",
            url=f"/catalog/works/{work_id}",
            path_params={"work_id": work_id},
        )
    )

    assert response.status_code == 200
    assert response.body == {"id": work_id}
    assert use_case.work_id.value == work_id


@pytest.mark.asyncio
async def test_get_all_works_controller_returns_collection() -> None:
    use_case = UseCaseSpy({"works": [{"id": "work-id"}]})
    controller = GetAllWorksController(use_case)

    response = await controller.handle_request(
        HttpRequest(method="GET", url="/catalog/works")
    )

    assert response.status_code == 200
    assert response.body == {"works": [{"id": "work-id"}]}
    assert use_case.work_id is None


@pytest.mark.asyncio
async def test_replace_work_cover_controller_maps_id_and_file_metadata() -> None:
    work_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    use_case = UseCaseSpy({"id": work_id, "cover_image_url": "signed-url"})
    controller = ReplaceWorkCoverController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="PUT",
            url=f"/catalog/works/{work_id}/cover",
            path_params={"work_id": work_id},
            body={
                "content": object(),
                "content_type": "image/png",
                "size_bytes": 100,
            },
        )
    )

    assert response.status_code == 200
    assert use_case.work_id.work_id.value == work_id
    assert use_case.work_id.content_type == "image/png"


@pytest.mark.asyncio
async def test_remove_work_cover_controller_maps_id() -> None:
    work_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    use_case = UseCaseSpy({"id": work_id, "cover_image_url": None})
    controller = RemoveWorkCoverController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="DELETE",
            url=f"/catalog/works/{work_id}/cover",
            path_params={"work_id": work_id},
        )
    )

    assert response.status_code == 200
    assert use_case.work_id.work_id.value == work_id
