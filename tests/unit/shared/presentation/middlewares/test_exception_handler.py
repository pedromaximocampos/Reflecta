import pytest

from src.shared.domain.errors.domain_error import DomainError
from src.shared.presentation.middlewares.exception_handler import ExceptionHandler


_EXPECTED_UNEXPECTED_ERROR = {
    "errors": [
        {
            "title": "UnexpectedError",
            "status": 500,
            "data": "Não foi possível concluir a solicitação. Tente novamente.",
            "details": None,
        }
    ],
    "meta": {},
}


@pytest.mark.parametrize(
    "error",
    [
        RuntimeError("AWS credential details must never reach the client"),
        DomainError(
            message="private infrastructure failure",
            status_code=500,
            name="PrivateInfrastructureError",
        ),
    ],
)
def test_unexpected_errors_use_safe_standard_response(error: Exception) -> None:
    response = ExceptionHandler.handle_exception(error)

    assert response.status_code == 500
    assert response.body == _EXPECTED_UNEXPECTED_ERROR
    assert "AWS" not in str(response.body)
    assert "private infrastructure" not in str(response.body)


def test_client_domain_errors_keep_their_public_contract() -> None:
    error = DomainError(
        message="Public validation message",
        status_code=422,
        name="ValidationError",
    )

    response = ExceptionHandler.handle_exception(error)

    assert response.status_code == 422
    assert response.body["errors"][0] == {
        "title": "ValidationError",
        "status": 422,
        "data": "Public validation message",
        "details": None,
    }
