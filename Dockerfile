FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.31 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY pyproject.toml uv.lock /app/
COPY src/ /app/src/
COPY database/ /app/database/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

ENTRYPOINT []