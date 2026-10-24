# Power BI report — reproducible build specification

**Status:** a full native `.pbix` has NOT yet been generated. These are instructions, data contracts and DAX measures for a three-page Power BI Desktop report. Do not describe a published Power BI dashboard on a CV before opening and validating the report in Desktop.

## Source contract

After the GitHub Action `Build real UCI retail analysis` succeeds, the following files should be committed:
- `powerbi/data/invoices.csv` — unique invoice grain; `invoice_no, invoice_date, country, customer_id, order_month, order_revenue, sku_count`
- `powerbi/data/monthly_sales.csv` — one row per YYYY-MM
- `powerbi/data/country_sales.csv` — one row per country
- `powerbi/data/product_sales.csv` — SKU/description totals
- `powerbi/data/rfm.csv` — identifiable customer grain
- `powerbi/data/cohort_retention.csv` — month of first order × months since first order
- `powerbi/data/data_quality.csv` — data-quality metrics and counts

Alternatively, run the scripts locally and import these files from `data/processed/` and `reports/02_cohorts.csv`.

**Before first successful real-data run**, these files do not exist on the main branch.

## Build steps

1. Open Power BI Desktop → Blank report → Home → Get data → Text/CSV.
2. Import the seven CSVs above; name tables `invoices, monthly_sales, country_sales, product_sales, rfm, cohort_retention, data_quality`.
3. In Power Query set `invoices[invoice_no]`, `invoices[customer_id]` and `rfm[customer_id]` to Text; `invoices[order_revenue]`, `rfm[monetary]` and sales aggregates to Decimal Number; `invoices[invoice_date]` to Date/Time. Set `cohort_retention[month_index]` and `cohort_retention[active_customers]` to Whole Number.
4. Add measures (create separately):
```dax
Gross Merchandise Sales = SUM(invoices[order_revenue])
Orders = DISTINCTCOUNT(invoices[invoice_no])
Average Order Value = DIVIDE([Gross Merchandise Sales], [Orders])
Identified Buyers = DISTINCTCOUNT(rfm[customer_id])
Repeat Buyers = CALCULATE(COUNTROWS(rfm), rfm[frequency] >= 2)
Repeat Buyer Share = DIVIDE([Repeat Buyers], [Identified Buyers])
```
5. Create report with three pages following specifications below.
6. Use a prominent subtitle: **UCI Online Retail, Dec 2010 – Dec 2011; gross positive merchandise sales only; not net revenue or profit**.
7. Validate all KPI cards against `reports/analysis_summary.md` after the *real* pipeline completes. Verify exact figures and confirm the summary title says `UCI ONLINE RETAIL DATA`.
8. Save the native report as `powerbi/Retail_Sales_Customer_Analytics.pbix` and commit it with a screenshot only after testing.

## Page 1 — Sales performance

Design: top KPI row; trend visualization; side-by-side country/product ranking.

- Cards: Gross Merchandise Sales (GBP), Orders, Average Order Value
- Line chart: `monthly_sales[order_month]` → `monthly_sales[gross_sales]`; sort chronologically
- Bar chart: Top 10 `product_sales[description]` by `product_sales[gross_sales]`
- Bar chart: `country_sales[country]` by `country_sales[gross_sales]`
- Note: first and last calendar months are partial, so seasonal comparisons are descriptive

## Page 2 — Customers & retention

- Cards: Identified Buyers, Repeat Buyer Share
- Column chart: `rfm[segment]` by count of `rfm[customer_id]`
- Scatter: `rfm[frequency]` vs `rfm[monetary]`, bubble size by `rfm[recency_days]` (limit visible points)
- Cohort matrix: `cohort_retention[cohort_month]` rows, `cohort_retention[month_index]` columns, `cohort_retention[active_customers]` values. Add normalization to cohort 0 to display retention %; exclude future/nonexistent cells from the denominator
- Note: customers with missing IDs are excluded from repeat and RFM metrics

## Page 3 — Data-quality audit

- Table: `data_quality[metric]` and `data_quality[value]`
- KPI cards: exact duplicates, cancellation rows, missing CustomerID rows, clean merchandise rows
- Text explanation for exclusions: cancellations and nonpositive quantity/price, service codes, exact duplicates
- These counters overlap: **do not sum them as mutually exclusive removal reasons**

## Analytical safeguards

- Gross merchandise sales = positive quantity × unit price, excluding cancelled invoices and some non-merchandise codes; returns are reported separately
- Gross merchandise sales are **not** net revenue, profit, or cash receipts
- Cancelled invoice amounts are **proxies**, not payment processor refund evidence
- Historical records ending December 9, 2011 cannot identify future lifetime value
- RFM segments are heuristic; they do not demonstrate campaign causality

## Completion checklist

- [ ] GitHub workflow passes with original UCI data
- [ ] Real-data KPI values reconciled between Python and SQL
- [ ] Seven real-data CSVs available
- [ ] Power BI Desktop report built and visually reviewed
- [ ] `.pbix` committed, screenshot from Power BI (not Python) added
