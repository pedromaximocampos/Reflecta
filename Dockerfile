FROM python:3.14-slim

# Criando o diretorio de trabalho no caso app (convensao)
WORKDIR /app

# 1) instala uv buscando diretamente do astral (como recomendar
COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

# 2) copia arquivos de dependência primeiro (cache de build fica ótimo)
COPY pyproject.toml uv.lock ./

# 3) Equivalente ao pip install -r requirements.txt
RUN uv sync --locked


# 4) agora copia o código de interesse no caso o src/ src/
COPY src/ src/


