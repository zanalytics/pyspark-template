import shutil
from pathlib import Path

import pytest
from loguru import logger
from pyspark.sql import SparkSession

from pyspark_template.config.spark_session import create_spark_environment


def clean_databases() -> None:
    """Remove all databases and metafiles created by Spark."""
    db_paths = [
        Path("data/bronze.db"),
        Path("data/silver.db"),
        Path("data/gold.db"),
        Path("metastore_db"),
        Path("derby.log"),
    ]

    for db_path in db_paths:
        try:
            if db_path.is_dir():
                shutil.rmtree(db_path)
            elif db_path.exists():
                db_path.unlink()
        except PermissionError:
            logger.info(f"PermissionError: Unable to delete {db_path}")


@pytest.fixture(scope="session")
def spark_session() -> SparkSession:
    """Create a Spark session for testing."""
    spark = create_spark_environment(
        warehouse_dir="tests/data/",
        seed_directory="tests/data/seed",
    )
    yield spark
    spark.stop()
    clean_databases()


@pytest.fixture(scope="session")
def first_number(spark_session: SparkSession) -> int:
    """First number.

    Returns
    -------
    int
        A number

    """
    return 5
