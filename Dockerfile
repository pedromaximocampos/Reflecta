FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

RUN groupadd --system reflecta \
    && useradd --system --gid reflecta --home-dir /app reflecta

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY --chown=reflecta:reflecta alembic.ini ./
COPY --chown=reflecta:reflecta alembic/ alembic/
COPY --chown=reflecta:reflecta src/ src/

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER reflecta

CMD ["uvicorn", "src.main.server.fast_api.run:app", "--host", "0.0.0.0", "--port", "8000"]


