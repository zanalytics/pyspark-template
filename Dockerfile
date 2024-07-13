# Arguments for versioning
ARG SPARK_VERSION=3.5.1
ARG PYTHON_VERSION=3.11
ARG DELTA_SPARK_VERSION=3.2.0
ARG POETRY_VERSION=1.3.1
ARG FUNCTION_DIR="app"

###############################################
# Spark Base Image
###############################################
FROM debian:bullseye-slim AS spark-base
ARG SPARK_VERSION=3.5.1
# Install Java and other dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Download and install Spark
RUN curl -O https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark \
    && rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

###############################################
# Python Base Image
###############################################
FROM python:${PYTHON_VERSION}-slim-bullseye AS python-base
ARG POETRY_VERSION=1.3.1
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image
###############################################
FROM python-base AS builder-base
ARG FUNCTION_DIR="app"
# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry --version

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# Export poetry dependencies to requirements.txt, including all groups
RUN poetry export -f requirements.txt --output $PYSETUP_PATH/requirements.txt --without-hashes --with dev

###############################################
# Final Image
###############################################
FROM spark-base AS final
ARG PYSETUP_PATH="/opt/pysetup"
# Copy Python environment from python-base
COPY --from=python-base /usr/local /usr/local

# Copy built artifacts from builder-base
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Set the working directory in the container
WORKDIR app

# Copy the current directory contents into the container at /${FUNCTION_DIR}
COPY . /app

# Install the exported requirements and Delta Spark
RUN pip install --no-cache-dir -r /opt/pysetup/requirements.txt
