# Use a slim Python image for a smaller footprint
FROM python:3.11-slim-buster

RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy poetry.lock and pyproject.toml to ensure consistent dependencies
COPY poetry.lock pyproject.toml ./

# Install dependencies using poetry
RUN poetry install --no-interaction --no-ansi

# Copy the source code
COPY . .

# Expose the port where your Flask app typically runs (adjust if needed)
EXPOSE 8082

ENV FLASK_APP=main.py

# Set the main entrypoint to run the Flask app
CMD [ "poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8082" ]
