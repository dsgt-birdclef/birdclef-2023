import os
import sys
from contextlib import contextmanager

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def get_spark(cores=8, memory="8g"):
    """Get a spark session for a single driver."""
    return (
        SparkSession.builder.config("spark.driver.memory", memory)
        .config("spark.driver.cores", cores)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


@contextmanager
def spark_resource(*args, **kwargs):
    """A context manager for a spark session."""
    spark = get_spark(*args, **kwargs)
    try:
        yield spark
    finally:
        spark.stop()
