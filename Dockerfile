# syntax=docker/dockerfile:1

# Use an official lightweight Python image.
ARG PYTHON_VERSION=3.11.3
FROM python:${PYTHON_VERSION}-slim as base

# Prevent Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED=1

# Set up working directory
WORKDIR /app

# Create a virtual environment and activate it
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# You can perform operations that require root permissions here
# For example, installing system dependencies (if any)

# Copy Pipfile and Pipfile.lock and install dependencies as root
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

# Copy the source code into the container
COPY . .

# Optionally, create a non-privileged user for running the application
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Correct permissions for the application directory
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user for running the application
USER appuser

# Expose the port your app runs on
EXPOSE 5000

# Run the application using pipenv to ensure the virtual environment is activated
CMD ["pipenv", "run", "python", "app.py"]