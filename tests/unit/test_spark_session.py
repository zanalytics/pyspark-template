import pytest
from pyspark.sql.functions import col, lit

# Assuming you have a fixture named 'spark' that provides a SparkSession

def test_spark_dataframe_operations(spark_session):
    """Tests DataFrame operations."""
    # Create a sample DataFrame
    data = [("Alice", 28), ("Bob", 35), ("Charlie", 42)]
    columns = ["name", "age"]
    spark = spark_session
    df = spark.createDataFrame(data, columns) # noqa: PD901

    # Test 1: Check if the DataFrame has the correct number of rows
    assert df.count() == 3, "DataFrame should have 3 rows"

    # Test 2: Check if the DataFrame has the correct columns
    assert df.columns == ["name", "age"], "DataFrame should have 'name' and 'age' columns" # noqa: E501

    # Test 3: Test a simple transformation
    df_transformed = df.withColumn("age_next_year", col("age") + lit(1))
    result = df_transformed.filter(col("name") == "Alice").select("age_next_year").collect() # noqa: E501
    assert result[0]["age_next_year"] == 29, "Alice's age next year should be 29" # noqa: E501

    # Test 4: Test aggregation
    avg_age = df.agg({"age": "avg"}).collect()[0]["avg(age)"]
    assert avg_age == pytest.approx(35.0), "Average age should be approximately 35" # noqa: E501

    # Test 5: Test DataFrame schema
    schema = df.schema
    assert schema["name"].dataType.simpleString() == "string", "Name column should be of string type" # noqa: E501
    assert schema["age"].dataType.simpleString() == "bigint", "Age column should be of bigint type" # noqa: E501
