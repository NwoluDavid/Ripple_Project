# Use the official Python image as the base image
FROM python:3.12-slim

# Install Curl
RUN apt-get update && apt-get install -y curl

# Set the working directory to /app
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy the poetry.lock and pyproject.toml files to the container
COPY ./poetry.lock ./pyproject.toml /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

# Copy the prestart script to the container
COPY ./prestart.sh /app/

# Make the prestart script executable
RUN chmod +x /app/prestart.sh

# Copy the entire project to the container
COPY ./app /app/app

# Set the entrypoint to the prestart script
ENTRYPOINT ["/app/prestart.sh"]

# Set the default command to start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
