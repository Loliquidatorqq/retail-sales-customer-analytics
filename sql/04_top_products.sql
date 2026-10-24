-- Top products by merchandise revenue. StockCode protects against duplicate names.
SELECT stock_code, MIN(description) AS item_name,
       ROUND(SUM(line_revenue),2) AS gross_sales_gbp, SUM(quantity) AS units
FROM sales GROUP BY stock_code ORDER BY gross_sales_gbp DESC LIMIT 15;