import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import re
from datetime import datetime

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define the log parsing function
def parse_apache_log(log_line):
    """
    Parse Apache log line using regex pattern
    Format: IP - - [timestamp] "request" status bytes "user_agent"
    """
    pattern = r'^(\S+) - - \[([^\]]+)\] "([^"]*)" (\d+) (\d+) "([^"]*)"'
    match = re.match(pattern, log_line)
    
    if match:
        ip, timestamp_str, request, status, bytes_sent, user_agent = match.groups()
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            date = timestamp.date()
            hour = timestamp.hour
        except:
            timestamp = None
            date = None
            hour = None
        
        # Parse request
        request_parts = request.split()
        method = request_parts[0] if len(request_parts) > 0 else None
        url = request_parts[1] if len(request_parts) > 1 else None
        protocol = request_parts[2] if len(request_parts) > 2 else None
        
        return {
            'ip_address': ip,
            'timestamp': timestamp_str,
            'date': str(date) if date else None,
            'hour': hour,
            'method': method,
            'url': url,
            'protocol': protocol,
            'status_code': int(status),
            'bytes_sent': int(bytes_sent),
            'user_agent': user_agent,
            'raw_log': log_line
        }
    else:
        # Return None for unparseable lines
        return None

# Register the UDF
parse_log_udf = udf(parse_apache_log, StructType([
    StructField("ip_address", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("date", StringType(), True),
    StructField("hour", IntegerType(), True),
    StructField("method", StringType(), True),
    StructField("url", StringType(), True),
    StructField("protocol", StringType(), True),
    StructField("status_code", IntegerType(), True),
    StructField("bytes_sent", IntegerType(), True),
    StructField("user_agent", StringType(), True),
    StructField("raw_log", StringType(), True)
]))

# Read raw logs from S3
raw_logs = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": ["s3://website-log-analytics-project/raw-logs/"],
        "recurse": True
    },
    format="text"
)

# Convert to Spark DataFrame for easier processing
raw_df = raw_logs.toDF()

# Parse logs using the UDF
parsed_df = raw_df.select(parse_log_udf(col("text")).alias("parsed_log"))

# Flatten the parsed data
flattened_df = parsed_df.select(
    col("parsed_log.ip_address"),
    col("parsed_log.timestamp"),
    col("parsed_log.date"),
    col("parsed_log.hour"),
    col("parsed_log.method"),
    col("parsed_log.url"),
    col("parsed_log.protocol"),
    col("parsed_log.status_code"),
    col("parsed_log.bytes_sent"),
    col("parsed_log.user_agent"),
    col("parsed_log.raw_log")
)

# Filter out unparseable logs
cleaned_df = flattened_df.filter(col("ip_address").isNotNull())

# Add additional derived columns
enriched_df = cleaned_df.withColumn(
    "is_error", 
    when(col("status_code") >= 400, True).otherwise(False)
).withColumn(
    "is_success", 
    when(col("status_code") >= 200, True).otherwise(False)
).withColumn(
    "file_extension",
    when(col("url").isNotNull(), 
         regexp_extract(col("url"), r'\.([a-zA-Z0-9]+)(\?|$)', 1)
    ).otherwise(None)
).withColumn(
    "page_category",
    when(col("url").like("%/api/%"), "api")
    .when(col("url").like("%/admin/%"), "admin")
    .when(col("url").like("%/static/%"), "static")
    .when(col("url").like("%/images/%"), "images")
    .when(col("url").like("%/css/%"), "css")
    .when(col("url").like("%/js/%"), "js")
    .otherwise("page")
)

# Convert back to DynamicFrame
processed_dynamic_frame = DynamicFrame.fromDF(enriched_df, glueContext, "processed_logs")

# Write to S3 in Parquet format
glueContext.write_dynamic_frame.from_options(
    frame=processed_dynamic_frame,
    connection_type="s3",
    connection_options={
        "path": "s3://website-log-analytics-project/glue-output/parquet/",
        "partitionKeys": ["date"]
    },
    format="parquet"
)

# Commit the job
job.commit()

print("Glue ETL job completed successfully!")
print(f"Processed logs written to: s3://website-log-analytics-project/glue-output/parquet/") 