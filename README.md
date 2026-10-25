# Retail Sales & Customer Analytics

**SQL (SQLite) · Python/pandas · Power BI-ready data model · Customer segmentation**

An end-to-end **educational business analytics case** built around transactions from an online gift retailer. It answers four practical questions: *How are sales developing? Which products and markets matter? Who buys again? Which customers should retention teams prioritize?*

**Data status: VERIFIED REAL UCI DATA.** The GitHub Actions pipeline processed all 541,909 source rows. Python transformations, unit tests and SQL queries completed successfully. Exported real-data tables are in `powerbi/data/`, validated summary in `reports/analysis_summary.md`. The original raw workbook is intentionally not redistributed.

**Portfolio stage:** verified real-data analysis and visual summaries are published. The three-page Power BI Desktop report is published in [`powerbi/Retail_Sales_Customer_Analytics.pbix`](powerbi/Retail_Sales_Customer_Analytics.pbix).

## Verified real-data results (UCI Online Retail)

| Measure | Verified result |
| --- | ---: |
| Original transaction lines | 541,909 |
| Positive merchandise lines after filters/deduplication | 522,569 |
| Gross positive merchandise sales | **£10,258,967.19** |
| Orders | **19,774** |
| Average order value | **£518.81** |
| Identified customers | **4,334** |
| Repeat-buyer share of identified customers | **65.3%** |
| Original cancellation invoice lines | 9,288 |

**Business findings:** November 2011 had the highest monthly gross merchandise sales (£1,452,115.98), while first and final months of this extract are partial. The UK contributed £8,736,191.54 (~85.2%) of observed gross positive merchandise sales. Customer segmentation and cohort counts can inform hypotheses for loyalty/reactivation, but do not establish a causal effect. These figures are *descriptive*, exclude cancellations from gross sales, and are **not net revenue/profit**.

![RFM segmentation of identified customers](figures/rfm_segments.png)
![Top countries by gross merchandise sales](figures/sales_by_country.png)

**Interactive standalone preview:** [`dashboard/retail-analytics-real.html`](dashboard/retail-analytics-real.html) (download and open in a browser). It is built from **verified real-data aggregates**, but is not a native Power BI report. The Power BI Desktop build instructions are in [`powerbi/REPORT_SETUP.md`](powerbi/REPORT_SETUP.md).

## 1. Business questions and KPIs

| Area | Analysis | Why a business stakeholder cares |
|---|---|---|
| Sales | Gross positive merchandise sales, orders, AOV, monthly changes | Sales planning and tracking seasonality |
| Product / geography | Ranking of SKUs and countries by merchandise sales | Identify sales concentration and priorities |
| Customers | Repeat-buyer share, purchase cohort, RFM segmentation | Campaign targeting and reactivation hypotheses |
| Data quality | Missing buyer IDs, cancellations, charges and duplicates | Avoid misleading KPIs |

**Critical distinction:** gross positive merchandise sales are not net revenue, profit or margin. Cancellations are recorded separately; costs and marketing spend are not supplied.

## 2. Data provenance

- **Official source:** [UCI Machine Learning Repository — Online Retail (ID 352)](https://archive.ics.uci.edu/dataset/352/online+retail)
- **Citation:** Chen, D. (2015). *Online Retail*. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
- **License:** source dataset **CC BY 4.0**. Code in this repo **MIT**.
- **Period:** December 1, 2010 to December 9, 2011 (first and last observation months are incomplete).
- **Rows:** 541,909 in official source; each row is a transaction **line item**, not an order.
- **Demo:** run `scripts/generate_demo.py` to create `data/demo/online_retail_demo.csv`, containing artificial customers and synthetic transactions. It is never used as evidence about the real business.

The full original UCI workbook is **not bundled** in this repo. Its original file can be retrieved by `scripts/download_uci.py`.

## 3. Reproduce the project

Python 3.10+ required. From the project root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Fast offline smoke test (SYNTHETIC DEMO)
python scripts/generate_demo.py
python scripts/run_pipeline.py --mode demo
python scripts/run_sql.py
python -m unittest discover -s tests -v

# To run on the REAL, original UCI workbook (requires internet)
python scripts/download_uci.py
python scripts/run_pipeline.py --mode real
python scripts/run_sql.py
```

You may also manually download `Online Retail.xlsx` from the UCI source page into `data/raw/Online Retail.xlsx` if the scripted request fails.

**Warning:** running the real pipeline replaces `data/processed/`, `database/retail_analysis.sqlite`, the charts and results with real-data output. This is intentional.

## 4. Tools and deliverables

```
retail-sales-customer-analytics/
├── data/                # generated demo / UCI input / processed CSV outputs
├── database/            # generated SQLite analytical database
├── scripts/             # demo generator, UCI downloader, ETL, charting, SQL runner
├── sql/                 # KPI, cohort, RFM, cancellation and window-function queries
├── powerbi/             # step-by-step Power BI build guide and DAX measures
├── notebooks/           # student-readable walkthrough
├── figures/             # static chart previews labelled by data mode
├── reports/             # generated KPIs, QA table, SQL query outputs
├── docs/                # methodology, limitations and resume blurb
└── tests/               # data-cleaning and metric unit tests
```

### SQL examples

- `sql/01_kpis.sql` — sales, orders, AOV
- `sql/02_cohorts.sql` — **CTEs** and customer retention cohorts
- `sql/03_rfm.sql` — segment-level metrics
- `sql/04_top_products.sql` — product ranking
- `sql/05_returns_quality.sql` — cancellation-line metrics
- `sql/06_customer_rank.sql` — **ROW_NUMBER window function** for country-specific customer ranking

### Python / pandas

The cleaning pipeline validates types, identifies cancellation invoices, excludes non-merchandise charges and nonpositive entries, drops exact-row duplicates, builds invoice- and customer-grain data tables and saves a SQLite database for SQL queries.

### Power BI

Prepared CSVs, DAX measures and instructions are in [`powerbi/`](powerbi/README.md).

> **Power BI status:** the [`Retail_Sales_Customer_Analytics.pbix`](powerbi/Retail_Sales_Customer_Analytics.pbix) dashboard is available with Sales Overview, Customer Analytics and Data Quality. The PNG previews here are Python charts, not Power BI screenshots.

## 5. Selected metrics and visuals

### REAL UCI DATA (verified pipeline)

[Full analysis summary](reports/analysis_summary.md) · [Monthly KPI results](reports/01_kpis.csv) · [Power BI-ready datasets](powerbi/data/) · [Dashboard build instructions](powerbi/REPORT_SETUP.md)

**A native Power BI report is included:** [`Retail_Sales_Customer_Analytics.pbix`](powerbi/Retail_Sales_Customer_Analytics.pbix). The project also includes real-data exports and DAX measures. Figures shown above are Python-generated, not Power BI screenshots.

## 6. Analytical boundaries

1. **Unknown customers:** an order without a customer ID contributes to sales KPIs, but cannot be used for customer retention/RFM.
2. **Returns:** invoice IDs starting with C show cancellations. Negative units × unit price is a **proxy**, not a reconciliation to real refunds. Gross sales exclude these records rather than netting them.
3. **No funnel/cost data:** do not infer conversion, acquisition costs, gross margin or profit.
4. **Historical/partial coverage:** source ends December 9, 2011; later months and post-extract behavior are not observable. Apparent recent customer churn can be right-censoring.
5. **Segmentation:** RFM groups are heuristic suggestions for targeting, not causal estimates of campaign uplift.

For full definitions see [methodology](docs/methodology.md).

## 7. Power BI report and portability

1. The completed `.pbix` has been uploaded to the `powerbi/` folder.
2. Open and refresh the report on another computer, updating local CSV source paths if necessary.
3. Optionally add screenshots captured from Power BI Desktop.

## Author

**Nikita Buribaev** · MiBA, Graduate School of Management, Saint Petersburg State University · [GitHub](https://github.com/Loliquidatorqq)