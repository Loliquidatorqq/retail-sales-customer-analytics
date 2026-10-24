-- Customer monthly purchase cohort + active buyers (identified customers only).
-- Incomplete observation windows can depress later retention columns.
WITH customer_months AS (
    SELECT DISTINCT customer_id, order_month
    FROM invoices
    WHERE customer_id IS NOT NULL
), first_purchase AS (
    SELECT customer_id, MIN(order_month) AS cohort_month
    FROM customer_months GROUP BY customer_id
), cohort_activity AS (
    SELECT f.cohort_month, c.customer_id, c.order_month,
        (CAST(SUBSTR(c.order_month,1,4) AS INTEGER)-CAST(SUBSTR(f.cohort_month,1,4) AS INTEGER))*12
        + CAST(SUBSTR(c.order_month,6,2) AS INTEGER)-CAST(SUBSTR(f.cohort_month,6,2) AS INTEGER) AS month_index
    FROM customer_months c JOIN first_purchase f USING(customer_id)
)
SELECT cohort_month, month_index, COUNT(DISTINCT customer_id) AS active_customers
FROM cohort_activity GROUP BY cohort_month, month_index
ORDER BY cohort_month, month_index;