from pyspark_template.config.spark_session import spark

spark.sql("SELECT * FROM bronze.drivers").show()
