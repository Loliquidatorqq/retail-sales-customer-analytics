# Methodology and business interpretation

## Questions
1. How much positive merchandise revenue was recorded and how did it change over time?
2. Which products and countries contribute most?
3. What portion of identifiable customers purchase more than once?
4. Which customer segments could receive retention or reactivation campaigns?
5. What are the most important data-quality limits?

## Definitions
**Positive merchandise revenue:** include invoice lines only when `InvoiceNo` does not start C, `Quantity > 0`, `UnitPrice > 0`, `InvoiceDate` parses, and `StockCode` is not an identified charge code. Drop exact duplicate rows. Currency GBP. This is gross positive merchandise sales, not net revenue.

**Orders:** distinct valid invoice numbers with at least one merchandise item; basket size sums positive line revenue. Customers can have multiple orders.

**Repeat buyer %:** distinct identified buyers with >=2 valid invoices / all identified buyers. This is neither retention rate nor conversion rate.

**RFM:** recency in days since last order relative to one day after last observed valid invoice, frequency as unique invoices, monetary as gross purchased merchandise. Quintiles are derived using percentile ranks; segmentation rules are heuristics, not verified campaign performance.

**Returns:** cancellation invoice starts with C; `abs(Quantity) * UnitPrice` is an approximate value and cannot be matched to a refund payment without external transaction keys. Therefore returns are analyzed separately, not deducted from gross sales.

**Cohorts:** customers are assigned the month of their first observed qualifying invoice (not necessarily lifetime first), cohort activity by observed purchase month. Censoring applies, especially near observation end.

## Pitfalls avoided
- Calling total merchandise sales "net profit" is incorrect.
- Missing customer IDs should not make gross sales disappear.
- Partial months should not be read as complete months.
- Grouping products only by description can mix SKUs with identical names.
- A raw-data row represents an item line, not one order.
- Synthetic demo metrics are strictly test results, not UCI findings.