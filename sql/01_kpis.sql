-- Monthly KPI: positive merchandise gross sales, orders and AOV
-- Cancellations are excluded, not netted against revenue.
SELECT order_month,
       ROUND(SUM(order_revenue), 2) AS gross_sales_gbp,
       COUNT(DISTINCT invoice_no) AS orders,
       ROUND(SUM(order_revenue) / COUNT(DISTINCT invoice_no), 2) AS avg_order_value_gbp
FROM invoices
GROUP BY order_month
ORDER BY order_month;