from unittest.mock import AsyncMock

import pytest

from src.modules.ai_processing.presentation.controllers import (
    ListWorkIngestionsController,
)
from src.shared.presentation.http_types import HttpRequest


class _Result:
    def to_dict(self):
        return {"ingestions": []}


@pytest.mark.asyncio
async def test_controller_maps_limit_and_returns_collection() -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _Result()
    controller = ListWorkIngestionsController(use_case)

    response = await controller.handle_request(
        HttpRequest(
            method="GET",
            url="/ai-processing/work-ingestions?limit=25",
            query_params={"limit": "25"},
        )
    )

    use_case.execute.assert_awaited_once_with(limit=25)
    assert response.status_code == 200
    assert response.body == {"ingestions": []}
