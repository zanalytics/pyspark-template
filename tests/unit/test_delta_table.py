import tempfile
from pathlib import Path

from delta import DeltaTable
from pyspark.sql.functions import col, lit


def test_delta_table_operations(spark_session):
    """Tests Delta table operations."""
    spark = spark_session
    # Create a temporary directory
    with (tempfile.TemporaryDirectory() as tmpdir):
        delta_table_path = Path(tmpdir/"delta_test_table")

        # Create a sample DataFrame
        data = [("Alice", 28), ("Bob", 35), ("Charlie", 42)]
        columns = ["name", "age"]
        df = spark.createDataFrame(data, columns) # noqa: PD901

        # Write the DataFrame to a Delta table
        df.write.format("delta",
                        ).mode("overwrite",
                               ).save(delta_table_path)

        # Test 1: Check if the Delta table was created successfully
        assert DeltaTable.isDeltaTable(
            spark,
            delta_table_path),"Delta table should be created"

        # Test 2: Read the Delta table and verify its content
        read_df = spark.read.format("delta").load(delta_table_path)
        assert read_df.count() == 3, "Delta table should have 3 rows"

        # Test 3: Update the Delta table
        delta_table = DeltaTable.forPath(spark, delta_table_path)
        delta_table.update(
            condition=col("name") == "Alice",
            set={"age": lit(29)},
        )

        # Verify the update
        updated_df = spark.read.format("delta").load(delta_table_path)
        alice_age = updated_df.filter(col("name") == "Alice").select("age").collect()[0]["age"] # noqa: E501
        assert alice_age == 29, "Alice's age should be updated to 29"

        # Test 4: Insert new data into the Delta table
        new_data = [("David", 45)]
        new_df = spark.createDataFrame(new_data, columns)
        delta_table.alias("old").merge(
            new_df.alias("new"),
            "old.name = new.name",
        ).whenNotMatchedInsert(values={
            "name": col("new.name"),
            "age": col("new.age"),
        }).execute()

        # Verify the insert
        merged_df = spark.read.format("delta").load(delta_table_path)
        assert merged_df.count() == 4, "Delta table should now have 4 rows"

        # Test 5: Time travel query
        delta_table.history().show()  # This will print the table history

        # Get the version number before the insert
        version_before_insert = \
        delta_table.history().filter(
            col("operation") == "MERGE",
        ).select("version").collect()[0]["version"] - 1

        # Query the table at the version before the insert
        df_at_version = spark.read.format("delta",
                                          ).option("versionAsOf",
                                                   version_before_insert,
                                                   ).load(delta_table_path)
        assert df_at_version.count() == 3, f"Delta table at version {version_before_insert} should have 3 rows" # noqa: E501
