# Analysis summary — SYNTHETIC DEMO (NOT REAL BUSINESS RESULTS)

**Source mode:** `demo`. Gross positive merchandise sales are not net sales or profit.

| KPI | Result | Definition |
|---|---:|---|
| Gross merchandise sales | £192,805.88 | Sum positive merchandise quantity × price; excludes cancellations and selected charges |
| Orders | 3,600 | Unique non-cancellation invoices with merchandise |
| Average order value | £53.56 | Gross merchandise sales ÷ orders |
| Identified customers | 648 | Buyers with nonempty customer ID |
| Repeat-buyer share (identified only) | 98.3% | Identified buyers with 2+ invoices ÷ identified buyers |
| Cancellation invoice lines (source) | 259 | Invoice starts C, quantity < 0, price > 0 |
| Rows retained as merchandise sales | 10,692 | After documented filters and exact-row dedupe |

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
| raw_rows                     |   11190 |
| exact_duplicate_rows         |       0 |
| cancellation_invoice_rows    |     259 |
| nonpositive_quantity_rows    |     259 |
| nonpositive_price_rows       |       0 |
| excluded_nonmerchandise_rows |     239 |
| missing_customer_id_rows     |     157 |
| invalid_invoice_date_rows    |       0 |
| clean_merchandise_rows       |   10692 |
| identified_sales_rows        |   10555 |