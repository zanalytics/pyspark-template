import os
from pathlib import Path
from typing import Optional

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


def create_temp_tables(spark: SparkSession, seed_directory: str) -> None:
    """Create temporary tables from parquet files in the seed directory.

    Parameters
    ----------
    directory : str, optional
        The directory containing the csv files (default is "./data/seed/").

    Returns
    -------
    None

    """
    directory_path = Path(seed_directory)
    spark.sql("CREATE DATABASE IF NOT EXISTS bronze")
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")
    spark.sql("CREATE DATABASE IF NOT EXISTS gold")

    for filepath in directory_path.glob("*.csv"):
        table_name = filepath.stem
        seed_df = spark.read.csv(str(filepath),
                                 header=True,
                                 inferSchema=True)
        seed_df.createOrReplaceTempView(table_name)
        spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS bronze.{table_name}
            AS SELECT * FROM {table_name}
        """, # noqa: S608
        )


def create_spark_environment(
    warehouse_dir: Optional[str] = "data/", #noqa: FA100
    seed_directory: str="./data/seed/",
) -> SparkSession:
    """Configure Spark session.

    Looks for the DATABRICKS_RUNTIME_VERSION environment variable to
    determine if the script is running on Databricks.

    Parameters
    ----------
    warehouse_dir : str, optional
        Directory path to use as the Spark SQL warehouse directory.

    Returns
    -------
    SparkSession
        Configured Spark session.

    """
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        spark = SparkSession.builder.appName("app").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        return spark

    builder = (
        SparkSession.builder.master("local[*]")
        .appName("app")
        .config("spark.sql.warehouse.dir", warehouse_dir)
        .config(
            "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .config("spark.sql.catalogImplementation", "hive")
        .enableHiveSupport()
    )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    create_temp_tables(spark=spark, seed_directory=seed_directory)
    return spark


spark = create_spark_environment()

if __name__ == "__main__":
    spark.sql("SHOW TABLES").show(truncate=False)
