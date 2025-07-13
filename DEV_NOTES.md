# Developer Notes - AWS Log Analytics Pipeline

## Personal Setup & Workflow

### AWS Account Setup
- [ ] Create/verify AWS account with appropriate permissions
- [ ] Set up AWS CLI in WSL: `aws configure`
- [ ] Ensure access to: S3, Glue, Athena, QuickSight, IAM

### Local Development Environment
- [ ] WSL2 + Ubuntu (already set up)
- [ ] Git CLI for version control
- [ ] VS Code (optional but recommended)
- [ ] Python 3.x for local script testing

---

## Detailed Step-by-Step Instructions

### Step 1: Create S3 Bucket Structure
```bash
# Create main bucket (replace with your unique bucket name)
aws s3 mb s3://website-log-analytics-project

# Create folder structure (S3 folders are created automatically when you upload files)
# Create empty .keep files to establish the folder structure:
echo "" > .keep
aws s3 cp .keep s3://website-log-analytics-project/raw-logs/.keep
aws s3 cp .keep s3://website-log-analytics-project/glue-output/.keep
aws s3 cp .keep s3://website-log-analytics-project/glue-output/parquet/.keep
aws s3 cp .keep s3://website-log-analytics-project/athena-results/.keep
rm .keep

# Alternative: Folders will be created automatically when you upload files to them
```

### Step 2: Generate Sample Log Data
```bash
# Create sample-logs directory first
mkdir -p sample-logs

# Create sample Apache log entries
cat > sample-logs/access_log_example.log << 'EOF'
192.168.1.1 - - [07/Jul/2025:13:45:22 +0000] "GET /about HTTP/1.1" 200 1234 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
192.168.1.2 - - [07/Jul/2025:13:45:23 +0000] "GET /contact HTTP/1.1" 404 1234 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
192.168.1.3 - - [07/Jul/2025:13:45:24 +0000] "POST /api/data HTTP/1.1" 200 5678 "curl/7.68.0"
EOF

# Upload to S3
aws s3 cp sample-logs/access_log_example.log s3://website-log-analytics-project/raw-logs/
```

### Step 3: Create Glue Crawler
1. Go to AWS Glue Console
2. Create Crawler:
   - Name: `log-analytics-crawler`
   - Data source: S3 bucket `s3://website-log-analytics-project/raw-logs/`
   - IAM Role: Create new or use existing with Glue permissions
   - Schedule: On demand
   - Output: Create new database `log_analytics_db`

### Step 4: Create Glue ETL Job
1. Create new ETL job in Glue Console
2. Use the Python script from `glue-scripts/transform_logs.py`
3. Configure:
   - IAM Role: Same as crawler
   - S3 source: `s3://website-log-analytics-project/raw-logs/`
   - S3 target: `s3://website-log-analytics-project/glue-output/parquet/`
   - Output format: Parquet

### Step 5: Set Up Athena
1. Go to Athena Console
2. Create workgroup: `log-analytics-workgroup`
3. Set up query result location: `s3://website-log-analytics-project/athena-results/`
4. Run crawler to create table schema
5. Test queries from `athena-queries/common_queries.sql`

### Step 6: Create QuickSight Dashboard
1. Go to QuickSight Console
2. Create new dataset from Athena
3. Connect to `log_analytics_db` database
4. Build visualizations:
   - Line chart: Hits over time
   - Pie chart: Status codes
   - Bar chart: Top IP addresses
   - Table: User agents

---

## Troubleshooting & Common Issues

### Glue Job Fails
- Check IAM permissions for Glue role
- Verify S3 bucket names and paths
- Check Python script syntax in Glue console

### Athena Query Errors
- Ensure crawler has run successfully
- Check table exists in Glue Data Catalog
- Verify S3 permissions for Athena

### QuickSight Connection Issues
- Check Athena permissions for QuickSight
- Verify dataset connection settings

---

## Cost Optimization Tips
- Use S3 lifecycle policies to move old data to cheaper storage
- Partition data by date in Glue for better Athena performance
- Monitor and clean up unused resources

---

## Portfolio Enhancement Ideas
- [ ] Add CloudWatch Events to trigger Glue jobs automatically
- [ ] Implement data partitioning by date
- [ ] Add geo-IP lookup functionality
- [ ] Create Terraform/CloudFormation templates for infrastructure as code
- [ ] Add monitoring and alerting with CloudWatch

---

## Personal Reminders
- Take screenshots at each step for portfolio
- Record a 2-3 minute demo video
- Update README.md with final results
- Document any AWS cost estimates
- Keep AWS credentials secure and never commit them

---

## Useful Commands
```bash
# Check S3 bucket contents
aws s3 ls s3://website-log-analytics-project/ --recursive

# Monitor Glue job status
aws glue get-job-runs --job-name your-job-name

# Check Athena query history
aws athena list-query-executions --work-group log-analytics-workgroup

# List Glue databases
aws glue get-databases

# List Glue tables in a database
aws glue get-tables --database-name log_analytics_db
``` 