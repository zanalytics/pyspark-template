.PHONY: help, install, pre-commit, test, check-tables, refresh-database
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies for the package for development
	poetry install
	poetry run pre-commit install

test:  ## Run the unit tests
	poetry run pytest -vv -p no:warnings

pre-commit:  ## Run the pre-commit hooks
	poetry run pre-commit run --all-files

check-tables:  ## Run the pre-commit hooks
	poetry run python pyspark_template/config/spark_session.py

refresh-database:  ## Delete the spark databases and metadata files
	bash clean_databases.sh
