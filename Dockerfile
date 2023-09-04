ARG IMAGE=python:3.10-alpine

FROM $IMAGE as builder

MAINTAINER Hossein Naderi <hossein-naderi@hotmail.com>

RUN pip install poetry==1.3.0

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY . /app

RUN poetry install --without dev

FROM $IMAGE as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src /app/src

ENTRYPOINT ["pctl"]
