-- Business-segment size, customer value, and order frequency
SELECT segment, COUNT(*) AS customers,
       ROUND(SUM(monetary), 2) AS gross_sales_from_customers_gbp,
       ROUND(AVG(frequency), 2) AS mean_orders,
       ROUND(AVG(recency_days), 1) AS mean_recency_days
FROM rfm GROUP BY segment ORDER BY gross_sales_from_customers_gbp DESC;