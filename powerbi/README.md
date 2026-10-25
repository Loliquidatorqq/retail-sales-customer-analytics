# Power BI — implementation guide

**Status:** a three-page native Power BI Desktop report has been built and uploaded: [`Retail_Sales_Customer_Analytics.pbix`](Retail_Sales_Customer_Analytics.pbix). The real-data CSV exports, DAX reference and build instructions are also included. Opening on another device may require updating local CSV source paths.

## Load data
1. Run `python scripts/run_pipeline.py --mode real` (after obtaining the UCI file) or `--mode demo` to test offline.
2. In Power BI Desktop choose **Home → Get data → Text/CSV** and import from `data/processed/`:
   - `invoices.csv` (one row / invoice)
   - `sales.csv` (one row / merchandise line)
   - `rfm.csv` (one row / customer)
   - `cancellations.csv` (one row / cancellation line)
3. Set `invoices[invoice_no]` and `sales[invoice_no]` to **Text** and create `invoices[invoice_no]` (1) → `sales[invoice_no]` (*) relation (same-case names may require renaming).
4. Create a calculated column in `invoices`: `InvoiceDay = DATEVALUE(invoices[invoice_date])`. Create a DAX calendar table: `Calendar = CALENDAR(MIN(invoices[InvoiceDay]), MAX(invoices[InvoiceDay]))`. Mark it as a date table and create a relationship `Calendar[Date]` (1) → `invoices[InvoiceDay]` (*).
5. For customer-level charting, use `rfm` alone; don't create bidirectional relationships.

## Main page — Sales overview
Cards: Gross merchandise sales, Orders, Average order value, Identified buyers, Repeat buyer %.
Charts: Monthly revenue line; top 10 SKUs; country sales. Slicers: month and country.

## Page 2 — Customer retention
Charts: RFM segment bars; recency distribution; acquisition cohort retention matrix (SQL query 02 exported to CSV).

## Page 3 — Data quality
Cards and table from `data_quality.csv`: cancelled invoice lines, missing IDs, excluded service lines.

## Important definitions
- **Gross merchandise sales** are positive product sales only. They do not account for refunds, shipping, margins or operational costs.
- Customer-based measures exclude unidentifiable purchases. The revenue card includes them.
- First/last real source months are partial, so show that caveat in the report.
- Calendar/date fields must be parsed using invariant locale `en-GB` or a suitable explicit parser if necessary.
- Add a banner `SYNTHETIC DEMO` when using demo files.

## DAX measures
Copy measures from [`measures.dax`](measures.dax) into a dedicated `Measures` table. Each expression is a separate measure (the file is not an executable bulk import).