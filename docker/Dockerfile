FROM python:3 as builder

RUN apt-get update && apt-get install -y pipx

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH=/root/.local/bin:$PATH

RUN pipx install poetry && pipx ensurepath --force

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN echo > README.md

RUN poetry install && rm -rf $POETRY_CACHE_DIR

FROM python:3 as runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:/root/.local/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY --from=builder /usr/bin/pipx /usr/bin/pipx 

COPY --from=builder /root/.local/pipx /root/.local/pipx

COPY --from=builder /root/.local/bin /root/.local/bin

COPY --from=builder /app .

COPY src/ .

CMD ["poetry", "run", "python", "./french_number_practice.py"]
