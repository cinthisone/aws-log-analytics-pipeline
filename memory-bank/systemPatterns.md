# System Patterns

## Architecture Overview
- Event-driven, serverless data pipeline
- S3 for storage (raw and processed logs)
- Glue for ETL (parsing, cleaning, transforming)
- Athena for ad-hoc SQL queries
- QuickSight for visualization

## Key Technical Decisions
- Use Parquet for efficient storage and querying
- Partition data by date for cost/performance
- Use Glue Data Catalog for schema management

## Design Patterns
- ETL as code (Glue scripts in version control)
- Infrastructure as code (optionally, for bonus DevOps points)
- Modular folder structure for clarity 