-- Athena Common Queries for Processed Web Access Logs
-- Assumes table is in log_analytics_db and named date_2025_07_07

-- 1. Total requests per day
SELECT substr(timestamp, 1, 10) AS log_date, COUNT(*) AS total_requests
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY substr(timestamp, 1, 10)
ORDER BY log_date;

-- 2. Top 10 IP addresses by request count
SELECT ip_address, COUNT(*) AS request_count
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY ip_address
ORDER BY request_count DESC
LIMIT 10;

-- 3. Most requested URLs
SELECT url, COUNT(*) AS hits
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY url
ORDER BY hits DESC
LIMIT 10;

-- 4. Error rate over time
SELECT substr(timestamp, 1, 10) AS log_date,
       COUNT(*) AS total,
       SUM(CASE WHEN is_error THEN 1 ELSE 0 END) AS errors,
       ROUND(100.0 * SUM(CASE WHEN is_error THEN 1 ELSE 0 END) / COUNT(*), 2) AS error_rate_percent
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY substr(timestamp, 1, 10)
ORDER BY log_date;

-- 5. Status code distribution
SELECT status_code, COUNT(*) AS count
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY status_code
ORDER BY count DESC;

-- 6. User agent breakdown
SELECT user_agent, COUNT(*) AS count
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY user_agent
ORDER BY count DESC
LIMIT 10;

-- 7. Requests by page category
SELECT page_category, COUNT(*) AS count
FROM "log_analytics_db"."date_2025_07_07"
GROUP BY page_category
ORDER BY count DESC; 