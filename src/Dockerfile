# dockerfile for building the api-server

FROM python:3.11-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /src

COPY pyproject.toml ./
# run poetry install
RUN poetry install

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]