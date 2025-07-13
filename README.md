# AWS Log Analytics Pipeline

## Overview
This project demonstrates a serverless data analytics pipeline on AWS, designed to collect, process, analyze, and visualize website access logs using S3, Glue, Athena, and QuickSight. It is ideal for showcasing data engineering and DevOps skills in your portfolio.

---

## Architecture
```
s3://website-log-analytics/
├── raw-logs/
│   └── access_logs_YYYY-MM-DD.log
├── glue-output/
│   └── parquet/
└── athena-results/
```
- **S3**: Stores raw and processed logs
- **Glue**: ETL jobs to parse and transform logs
- **Athena**: SQL queries on processed data
- **QuickSight**: Dashboards and visualizations

---

## Tools Used
- AWS S3
- AWS Glue
- AWS Athena
- AWS QuickSight
- Python (for Glue scripts)
- SQL (for Athena queries)

---

## Step-by-Step Guide

### 1. Simulate or Collect Logs
- Generate or download sample Apache/Nginx log files.
- Upload them to `s3://website-log-analytics/raw-logs/`.

### 2. Create a Glue Crawler
- Point to the `raw-logs/` S3 folder.
- Use a built-in or custom classifier to parse the log format.
- Save the schema to the Glue Data Catalog.

### 3. Create a Glue Job
- Transform raw log lines into structured format (e.g., Parquet):
  ```json
  {
    "ip_address": "192.168.1.1",
    "timestamp": "2025-07-07T13:45:22+00:00",
    "hour": 13,
    "method": "GET",
    "url": "/about",
    "protocol": "HTTP/1.1",
    "status_code": 200,
    "bytes_sent": 1234,
    "user_agent": "Mozilla/5.0",
    "raw_log": "192.168.1.1 - - [07/Jul/2025:13:45:22 +0000] \"GET /about HTTP/1.1\" 200 1234 \"Mozilla/5.0\"",
    "is_error": false,
    "is_success": true,
    "file_extension": "",
    "page_category": "page"
  }
  ```
- Store results in `s3://website-log-analytics/glue-output/parquet/`.

### 4. Query with Athena
- Point Athena to the `glue-output/parquet/` location.
- Use the Glue Catalog table.
- Example query:
  ```sql
  SELECT status_code, COUNT(*) as count 
  FROM "log_analytics_db"."date_2025_07_07"
  GROUP BY status_code 
  ORDER BY count DESC;
  ```

### 5. Visualize with QuickSight
- Connect QuickSight to the Athena database.
- Build dashboards (hits over time, top IPs, error rates, user agents, etc.).

---

## Portfolio Tips
- Include sample log data, Glue scripts, Athena queries, and screenshots in your repo.
- Add an architecture diagram and a video walkthrough for extra impact.
- Document your workflow and decisions in the `memory-bank/` folder.

---

## Real-World Use Cases
- Website traffic monitoring
- Security and error analysis
- Business intelligence from web logs

---

## Getting Started
1. Clone this repo and review the folder structure.
2. Follow the step-by-step guide above.
3. Update the README with your results and screenshots.

---

## License
MIT 