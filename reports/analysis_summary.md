# Analysis summary — UCI ONLINE RETAIL DATA

**Source mode:** `real`. Gross positive merchandise sales are not net sales or profit.

| KPI | Result | Definition |
|---|---:|---|
| Gross merchandise sales | £10,258,967.19 | Sum positive merchandise quantity × price; excludes cancellations and selected charges |
| Orders | 19,774 | Unique non-cancellation invoices with merchandise |
| Average order value | £518.81 | Gross merchandise sales ÷ orders |
| Identified customers | 4,334 | Buyers with nonempty customer ID |
| Repeat-buyer share (identified only) | 65.3% | Identified buyers with 2+ invoices ÷ identified buyers |
| Cancellation invoice lines (source) | 9,288 | Invoice starts C, quantity < 0, price > 0 |
| Rows retained as merchandise sales | 522,569 | After documented filters and exact-row dedupe |

## Data limitations

- Cancellation amount is a proxy (`abs(quantity) × unit_price`) and **not** a verified refund.
- Gross sales do not deduct cancellations; they exclude cancelled transactions.
- Missing customer IDs do not affect gross-sales totals but are omitted from customer segmentation.
- The first and last months of the full source are partial; month-over-month comparisons require caution.
- No costs, marketing spend, traffic, or product category labels are available. **Profit, ROI, conversion rate and customer acquisition cost cannot be measured** from these fields.
- **Demo source is simulated** and cannot be interpreted as a finding about the UCI retailer.

## Data quality counters (overlapping categories)

| metric                       |   value |
|:-----------------------------|--------:|
| raw_rows                     |  541909 |
| exact_duplicate_rows         |    5268 |
| cancellation_invoice_rows    |    9288 |
| nonpositive_quantity_rows    |   10624 |
| nonpositive_price_rows       |    2517 |
| excluded_nonmerchandise_rows |    2913 |
| missing_customer_id_rows     |  135080 |
| invalid_invoice_date_rows    |       0 |
| clean_merchandise_rows       |  522569 |
| identified_sales_rows        |  391150 |
