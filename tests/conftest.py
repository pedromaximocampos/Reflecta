import asyncio
import os

import pytest

from src.core.settings import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """
    Event loop único pra toda a suíte async.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """
    Settings globais no modo de teste.
    """
    os.environ["ENV"] = "test"
    return get_settings()


@pytest.fixture(autouse=True, scope="session")
def block_network():
    """
    Evita chamadas HTTP externas acidentais nos testes.
    Ajuste se necessário (ex: se não usar httpx).
    """
    monkeypatch = pytest.MonkeyPatch()

    def fake_get(*args, **kwargs):
        raise RuntimeError("Chamadas HTTP externas estão bloqueadas nos testes.")

    try:
        import httpx
        monkeypatch.setattr("httpx.get", fake_get, raising=False)
    except ImportError:
        pass
    yield
    monkeypatch.undo()
