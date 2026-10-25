"""Анализ продаж интернет-магазина на pandas и SQLite.

Usage:
    python scripts/run_pipeline.py --mode demo
    python scripts/download_uci.py
    python scripts/run_pipeline.py --mode real

Metrics are descriptive; they do not measure net sales, profitability or margin.
"""
from pathlib import Path
import argparse
import sqlite3
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_CODES = {'POST', 'DOT', 'BANK CHARGES', 'M', 'D', 'S', 'AMAZONFEE', 'CRUK', 'C2', 'PADS'}
REQUIRED = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']

def read_source(path):
    # Исходный файл может быть Excel или CSV.
    if not path.exists():
        raise FileNotFoundError(
            f'{path} not found. For real data first run: python scripts/download_uci.py'
        )

    text_columns = {
        'InvoiceNo': str,
        'StockCode': str,
        'CustomerID': str,
    }

    if path.suffix.lower() == '.xlsx':
        raw = pd.read_excel(path, dtype=text_columns)
    else:
        raw = pd.read_csv(path, dtype=text_columns)

    missing = set(REQUIRED) - set(raw.columns)
    if missing:
        raise ValueError(f'Missing required source columns: {sorted(missing)}')

    return raw


def transform(raw):
    # 1. Приводим исходные столбцы к нужным типам.
    data = raw[REQUIRED].copy()
    data['InvoiceNo'] = data['InvoiceNo'].astype('string').str.strip()
    data['StockCode'] = data['StockCode'].astype('string').str.strip().str.upper()
    data['Description'] = (
        data['Description'].astype('string').str.strip().fillna('UNKNOWN PRODUCT DESCRIPTION')
    )
    data['Country'] = data['Country'].astype('string').str.strip()
    data['CustomerID'] = (
        data['CustomerID'].astype('string').str.replace(r'\.0$', '', regex=True)
    )
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'], errors='coerce')

    for column in ['Quantity', 'UnitPrice']:
        data[column] = pd.to_numeric(data[column], errors='coerce')

    raw_rows = len(data)
    duplicate_rows = int(data.duplicated().sum())
    missing_customers = int(data['CustomerID'].isna().sum())

    # 2. Находим строки, которые не должны входить в валовые продажи.
    cancelled = data['InvoiceNo'].str.upper().str.startswith('C').fillna(False)
    wrong_date = data['InvoiceDate'].isna()
    wrong_quantity = data['Quantity'].le(0).fillna(True)
    wrong_price = data['UnitPrice'].le(0).fillna(True)
    service_code = data['StockCode'].isin(EXCLUDED_CODES)

    # Отмены сохраняем отдельно от продаж.
    refund_rows = cancelled & data['Quantity'].lt(0).fillna(False)
    refund_rows = refund_rows & data['UnitPrice'].gt(0).fillna(False)
    cancellations = data.loc[refund_rows].copy()
    cancellations['refund_value_proxy'] = (
        cancellations['Quantity'].abs() * cancellations['UnitPrice']
    ).round(2)

    valid = ~(cancelled | wrong_date | wrong_quantity | wrong_price | service_code)
    sales = data.loc[valid].drop_duplicates().copy()
    sales['line_revenue'] = (sales['Quantity'] * sales['UnitPrice']).round(2)
    sales['order_month'] = sales['InvoiceDate'].dt.strftime('%Y-%m')
    sales['invoice_date'] = sales['InvoiceDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    cancellations['invoice_date'] = (
        cancellations['InvoiceDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
    )

    column_names = {
        'InvoiceNo': 'invoice_no',
        'StockCode': 'stock_code',
        'Description': 'description',
        'Quantity': 'quantity',
        'UnitPrice': 'unit_price',
        'CustomerID': 'customer_id',
        'Country': 'country',
    }
    sales = sales.rename(columns=column_names).drop(columns='InvoiceDate')
    cancellations = cancellations.rename(columns=column_names).drop(columns='InvoiceDate')

    # 3. Собираем покупки: одна строка на один номер заказа.
    invoices = (
        sales.groupby('invoice_no', dropna=False)
        .agg(
            invoice_date=('invoice_date', 'min'),
            country=('country', 'first'),
            customer_id=('customer_id', 'first'),
            order_month=('order_month', 'first'),
            order_revenue=('line_revenue', 'sum'),
            sku_count=('stock_code', 'nunique'),
        )
        .reset_index()
    )
    invoices['order_revenue'] = invoices['order_revenue'].round(2)

    # 4. Считаем RFM только для покупателей с известным ID.
    known = invoices[invoices['customer_id'].notna()].copy()
    last_day = pd.to_datetime(invoices['invoice_date']).max().normalize()
    anchor = last_day + pd.Timedelta(days=1)

    rfm = (
        known.groupby('customer_id')
        .agg(
            latest_purchase=('invoice_date', 'max'),
            frequency=('invoice_no', 'nunique'),
            monetary=('order_revenue', 'sum'),
        )
        .reset_index()
    )

    if not rfm.empty:
        purchase_date = pd.to_datetime(rfm['latest_purchase']).dt.normalize()
        rfm['recency_days'] = (anchor - purchase_date).dt.days

        # Каждому RFM-показателю ставим балл от 1 до 5.
        rfm['r_score'] = 6 - np.ceil(
            rfm['recency_days'].rank(method='average', pct=True) * 5
        ).astype(int)
        rfm['f_score'] = np.ceil(
            rfm['frequency'].rank(method='average', pct=True) * 5
        ).astype(int)
        rfm['m_score'] = np.ceil(
            rfm['monetary'].rank(method='average', pct=True) * 5
        ).astype(int)

        def segment(customer):
            if customer.r_score >= 4 and customer.f_score >= 4 and customer.m_score >= 4:
                return 'Champions'
            if customer.f_score >= 4:
                return 'Loyal'
            if customer.r_score <= 2 and customer.f_score >= 3:
                return 'At risk'
            if customer.r_score >= 4 and customer.frequency == 1:
                return 'New customers'
            if customer.r_score >= 3:
                return 'Potential loyalists'
            return 'Hibernating'

        rfm['segment'] = rfm.apply(segment, axis=1)
    else:
        # Пустой результат тоже должен иметь нужные столбцы.
        rfm = rfm.assign(
            recency_days=pd.Series(dtype='int'),
            r_score=pd.Series(dtype='int'),
            f_score=pd.Series(dtype='int'),
            m_score=pd.Series(dtype='int'),
            segment=pd.Series(dtype='str'),
        )

    rfm['monetary'] = rfm['monetary'].round(2)

    # 5. Агрегируем продажи для отчёта Power BI.
    by_month = (
        invoices.groupby('order_month')
        .agg(
            gross_sales=('order_revenue', 'sum'),
            orders=('invoice_no', 'nunique'),
        )
        .reset_index()
    )
    by_month['aov'] = by_month['gross_sales'] / by_month['orders']
    by_month[['gross_sales', 'aov']] = by_month[['gross_sales', 'aov']].round(2)

    by_country = (
        sales.groupby('country')
        .agg(gross_sales=('line_revenue', 'sum'), units=('quantity', 'sum'))
        .reset_index()
        .sort_values('gross_sales', ascending=False)
    )
    by_product = (
        sales.groupby(['stock_code', 'description'])
        .agg(gross_sales=('line_revenue', 'sum'), units=('quantity', 'sum'))
        .reset_index()
        .sort_values('gross_sales', ascending=False)
    )
    for table in [by_country, by_product]:
        table['gross_sales'] = table['gross_sales'].round(2)

    # Категории ошибок могут пересекаться, поэтому их нельзя складывать.
    quality = pd.DataFrame(
        [
            ['raw_rows', raw_rows],
            ['exact_duplicate_rows', duplicate_rows],
            ['cancellation_invoice_rows', int(cancelled.sum())],
            ['nonpositive_quantity_rows', int(wrong_quantity.sum())],
            ['nonpositive_price_rows', int(wrong_price.sum())],
            ['excluded_nonmerchandise_rows', int(service_code.sum())],
            ['missing_customer_id_rows', missing_customers],
            ['invalid_invoice_date_rows', int(wrong_date.sum())],
            ['clean_merchandise_rows', len(sales)],
            ['identified_sales_rows', int(sales['customer_id'].notna().sum())],
        ],
        columns=['metric', 'value'],
    )

    return {
        'sales': sales,
        'cancellations': cancellations,
        'invoices': invoices,
        'rfm': rfm,
        'monthly_sales': by_month,
        'country_sales': by_country,
        'product_sales': by_product,
        'data_quality': quality,
    }


def outputs(tables, mode):
    folder = ROOT / 'data/processed'
    folder.mkdir(parents=True, exist_ok=True)
    (ROOT / 'database').mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ROOT / 'database/retail_analysis.sqlite') as con:
        for name, table in tables.items():
            table.to_csv(folder / f'{name}.csv', index=False)
            table.to_sql(name, con, if_exists='replace', index=False)
        con.executescript("""
        CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
        CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(order_month);
        CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(stock_code);
        CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
        """)
    invoices = tables['invoices']
    sales = tables['sales']
    rfm = tables['rfm']
    q = tables['data_quality']
    cancellations = tables['cancellations']
    gross = sales['line_revenue'].sum()
    num_orders = invoices['invoice_no'].nunique()
    identified = len(rfm)
    repeat = int((rfm['frequency'] >= 2).sum())
    text=f"""# Analysis summary — {"SYNTHETIC DEMO (NOT REAL BUSINESS RESULTS)" if mode=="demo" else "UCI ONLINE RETAIL DATA"}

**Source mode:** `{mode}`. Gross positive merchandise sales are not net sales or profit.\n
| KPI | Result | Definition |
|---|---:|---|
| Gross merchandise sales | £{gross:,.2f} | Sum positive merchandise quantity × price; excludes cancellations and selected charges |
| Orders | {num_orders:,} | Unique non-cancellation invoices with merchandise |
| Average order value | £{gross/num_orders:,.2f} | Gross merchandise sales ÷ orders |
| Identified customers | {identified:,} | Buyers with nonempty customer ID |
| Repeat-buyer share (identified only) | {100*repeat/identified if identified else 0:.1f}% | Identified buyers with 2+ invoices ÷ identified buyers |
| Cancellation invoice lines (source) | {len(cancellations):,} | Invoice starts C, quantity < 0, price > 0 |
| Rows retained as merchandise sales | {len(sales):,} | After documented filters and exact-row dedupe |

## Data limitations

- Cancellation amount is a proxy (`abs(quantity) × unit_price`) and **not** a verified refund.
- Gross sales do not deduct cancellations; they exclude cancelled transactions.
- Missing customer IDs do not affect gross-sales totals but are omitted from customer segmentation.
- The first and last months of the full source are partial; month-over-month comparisons require caution.
- No costs, marketing spend, traffic, or product category labels are available. **Profit, ROI, conversion rate and customer acquisition cost cannot be measured** from these fields.
- **Demo source is simulated** and cannot be interpreted as a finding about the UCI retailer.

## Data quality counters (overlapping categories)

{q.to_markdown(index=False) if hasattr(q,'to_markdown') else q.to_string(index=False)}
"""
    reports = ROOT / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'analysis_summary.md').write_text(text, encoding='utf-8')
    return {
        'gross': float(gross),
        'orders': num_orders,
        'aov': float(gross / num_orders),
        'repeat_rate': float(repeat / identified if identified else 0),
        'n_customers': identified,
        'mode': mode,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['demo', 'real'], default='demo')
    args = parser.parse_args()
    source_file = 'data/demo/online_retail_demo.csv' if args.mode == 'demo' else 'data/raw/Online Retail.xlsx'
    raw = read_source(ROOT / source_file)
    tables = transform(raw)
    results = outputs(tables, args.mode)
    print(f"Mode: {args.mode.upper()} | rows: {len(raw):,} | gross: £{results['gross']:,.2f} | orders: {results['orders']:,} | AOV: £{results['aov']:,.2f}")
    try:
        from charts import make_charts
        make_charts(tables, args.mode)
    except ImportError:
        print('Charts not generated (matplotlib is not installed).')

if __name__ == '__main__':
    main()