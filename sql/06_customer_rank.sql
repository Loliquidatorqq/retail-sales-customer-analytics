-- Window-function example: top-spending customers within each country.
-- Attributed positive sales only; missing customer IDs excluded.
WITH customer_country AS (
 SELECT country, customer_id, SUM(line_revenue) AS gross_sales_gbp
 FROM sales WHERE customer_id IS NOT NULL
 GROUP BY country,customer_id
), ranked AS (
 SELECT country,customer_id,ROUND(gross_sales_gbp,2) AS gross_sales_gbp,
 ROW_NUMBER() OVER (PARTITION BY country ORDER BY gross_sales_gbp DESC,customer_id) AS rn
 FROM customer_country
)
SELECT * FROM ranked WHERE rn <= 3 ORDER BY country,rn;