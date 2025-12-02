import os
import pytest
import asyncio
from pydantic_settings import BaseSettings
from uuid import uuid4
from src.core.settings import get_settings

# ------------------------------
# 1) Event loop para testes async
# ------------------------------
@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop próprio para os testes (pytest-asyncio exige isso)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()



@pytest.fixture(scope="session")
def settings():
    """Retorna configurações específicas para ambiente de teste."""
    os.environ["ENV"] = "test"
    return get_settings()


# ------------------------------
# 3) Factory útil para gerar IDs
# ------------------------------
@pytest.fixture
def new_id():
    """Gera um ID único sempre que for chamado."""
    return lambda: str(uuid4())


# ------------------------------
# 4) Segurança: bloquear requests externos
# ------------------------------
@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    """Impede testes de fazer chamadas HTTP externas sem querer."""
    def fake_get(*args, **kwargs):
        raise RuntimeError("Chamadas HTTP externas estão bloqueadas nos testes.")

    monkeypatch.setattr("httpx.get", fake_get)
    #monkeypatch.setattr("requests.get", fake_get)
