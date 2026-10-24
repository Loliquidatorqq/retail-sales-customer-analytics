-- Cancellation counts are descriptive; these are not verified refunds.
SELECT country, COUNT(*) AS cancellation_lines,
       ROUND(SUM(refund_value_proxy),2) AS cancellation_value_proxy_gbp
FROM cancellations GROUP BY country
ORDER BY cancellation_value_proxy_gbp DESC LIMIT 10;