# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
FROM python:3.12

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION="1.8.5" \
    POETRY_HOME=/opt/poetry \
    VIRTUAL_ENV="/venv"
ENV PATH="$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH"

RUN apt update && apt install -y vim jq less screen

# Install poetry into its own isolated virtualenv, separate from the application
# virtualenv it manages.
RUN python -m venv $POETRY_HOME \
    && pip install --no-cache-dir poetry==${POETRY_VERSION}

# Install dependencies into the activated application virtualenv ($VIRTUAL_ENV).
# The project itself is not installed (package-mode = false); the test group is
# included so the image can run the (integration) test suite via
# `docker compose run --rm safetynet pytest ...`.
RUN python -m venv $VIRTUAL_ENV
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root --with test

COPY docker/start.sh ./docker/start.sh
COPY queries.graphql schema.graphql ./
COPY safetynet ./safetynet

ENV ENVIRONMENT=production

CMD ["./docker/start.sh"]
