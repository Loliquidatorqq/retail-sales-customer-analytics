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
    if not path.exists():
        raise FileNotFoundError(f'{path} not found. For real data first run: python scripts/download_uci.py')
    if path.suffix.lower()=='.xlsx':
        raw=pd.read_excel(path,dtype={'InvoiceNo':str,'StockCode':str,'CustomerID':str})
    else:
        raw=pd.read_csv(path,dtype={'InvoiceNo':str,'StockCode':str,'CustomerID':str})
    missing=set(REQUIRED)-set(raw.columns)
    if missing:
        raise ValueError(f'Missing required source columns: {sorted(missing)}')
    return raw

def transform(raw):
    d=raw[REQUIRED].copy()
    d['InvoiceNo']=d['InvoiceNo'].astype('string').str.strip()
    d['StockCode']=d['StockCode'].astype('string').str.strip().str.upper()
    d['Description']=d['Description'].astype('string').str.strip().fillna('UNKNOWN PRODUCT DESCRIPTION')
    d['Country']=d['Country'].astype('string').str.strip()
    d['CustomerID']=d['CustomerID'].astype('string').str.replace(r'\.0$','',regex=True)
    d['InvoiceDate']=pd.to_datetime(d['InvoiceDate'],errors='coerce')
    for column in ['Quantity', 'UnitPrice']:
        d[column] = pd.to_numeric(d[column], errors='coerce')
    was=len(d)
    exact_duplicate_count=int(d.duplicated().sum())
    missing_customer_count=int(d.CustomerID.isna().sum())
    cancel=d.InvoiceNo.str.upper().str.startswith('C').fillna(False)
    invalid_date=d.InvoiceDate.isna()
    nonpositive_qty=d.Quantity.le(0).fillna(True)
    nonpositive_price=d.UnitPrice.le(0).fillna(True)
    excluded_stock=d.StockCode.isin(EXCLUDED_CODES)
    cancellations=d.loc[cancel & d.Quantity.lt(0).fillna(False) & d.UnitPrice.gt(0).fillna(False)].copy()
    cancellations['refund_value_proxy']=(cancellations.Quantity.abs()*cancellations.UnitPrice).round(2)
    # Учитываем только положительные товарные продажи. Возвраты считаем отдельно.
    valid=~(cancel|invalid_date|nonpositive_qty|nonpositive_price|excluded_stock)
    cleaned=d.loc[valid].drop_duplicates().copy()
    cleaned['line_revenue']=(cleaned.Quantity*cleaned.UnitPrice).round(2)
    cleaned['order_month']=cleaned.InvoiceDate.dt.strftime('%Y-%m')
    cleaned['invoice_date']=cleaned.InvoiceDate.dt.strftime('%Y-%m-%d %H:%M:%S')
    cancellations['invoice_date']=cancellations.InvoiceDate.dt.strftime('%Y-%m-%d %H:%M:%S')
    sales=cleaned.rename(columns={'InvoiceNo':'invoice_no','StockCode':'stock_code','Description':'description','Quantity':'quantity','UnitPrice':'unit_price','CustomerID':'customer_id','Country':'country'}).drop(columns='InvoiceDate')
    cancellations=cancellations.rename(columns={'InvoiceNo':'invoice_no','StockCode':'stock_code','Description':'description','Quantity':'quantity','UnitPrice':'unit_price','CustomerID':'customer_id','Country':'country'}).drop(columns='InvoiceDate')
    invoice=sales.groupby('invoice_no',dropna=False).agg(
        invoice_date=('invoice_date','min'),country=('country','first'),customer_id=('customer_id','first'),
        order_month=('order_month','first'),order_revenue=('line_revenue','sum'),sku_count=('stock_code','nunique')
    ).reset_index()
    invoice['order_revenue']=invoice.order_revenue.round(2)
    known=invoice[invoice.customer_id.notna()].copy()
    anchor=pd.to_datetime(invoice.invoice_date).max().normalize()+pd.Timedelta(days=1)
    rfm=known.groupby('customer_id').agg(
        latest_purchase=('invoice_date','max'),frequency=('invoice_no','nunique'),monetary=('order_revenue','sum')
    ).reset_index()
    if not rfm.empty:
        rfm['recency_days']=(anchor-pd.to_datetime(rfm.latest_purchase).dt.normalize()).dt.days
        # Баллы RFM: шкала от 1 до 5
        rfm['r_score']=6-np.ceil(rfm.recency_days.rank(method='average',pct=True)*5).astype(int)
        rfm['f_score']=np.ceil(rfm.frequency.rank(method='average',pct=True)*5).astype(int)
        rfm['m_score']=np.ceil(rfm.monetary.rank(method='average',pct=True)*5).astype(int)
        def segment(row):
            if row.r_score >= 4 and row.f_score >= 4 and row.m_score >= 4:
                return 'Champions'
            if row.f_score >= 4:
                return 'Loyal'
            if row.r_score <= 2 and row.f_score >= 3:
                return 'At risk'
            if row.r_score >= 4 and row.frequency == 1:
                return 'New customers'
            if row.r_score >= 3:
                return 'Potential loyalists'
            return 'Hibernating'
        rfm['segment']=rfm.apply(segment,axis=1)
    else:
        rfm=rfm.assign(recency_days=pd.Series(dtype='int'),r_score=pd.Series(dtype='int'),f_score=pd.Series(dtype='int'),m_score=pd.Series(dtype='int'),segment=pd.Series(dtype='str'))
    rfm['monetary']=rfm['monetary'].round(2)
    by_month=invoice.groupby('order_month').agg(gross_sales=('order_revenue','sum'),orders=('invoice_no','nunique')).reset_index()
    by_month['aov']=by_month.gross_sales/by_month.orders
    by_month[['gross_sales','aov']]=by_month[['gross_sales','aov']].round(2)
    by_country=sales.groupby('country').agg(gross_sales=('line_revenue','sum'),units=('quantity','sum')).reset_index().sort_values('gross_sales',ascending=False)
    by_product=sales.groupby(['stock_code','description']).agg(gross_sales=('line_revenue','sum'),units=('quantity','sum')).reset_index().sort_values('gross_sales',ascending=False)
    for group in [by_country, by_product]:
        group['gross_sales'] = group['gross_sales'].round(2)
    quality=pd.DataFrame([
        ['raw_rows',was],['exact_duplicate_rows',exact_duplicate_count],['cancellation_invoice_rows',int(cancel.sum())],
        ['nonpositive_quantity_rows',int(nonpositive_qty.sum())],['nonpositive_price_rows',int(nonpositive_price.sum())],
        ['excluded_nonmerchandise_rows',int(excluded_stock.sum())],['missing_customer_id_rows',missing_customer_count],
        ['invalid_invoice_date_rows',int(invalid_date.sum())],['clean_merchandise_rows',len(sales)],
        ['identified_sales_rows',int(sales.customer_id.notna().sum())]
    ],columns=['metric','value'])
    return {'sales':sales,'cancellations':cancellations,'invoices':invoice,'rfm':rfm,'monthly_sales':by_month,'country_sales':by_country,'product_sales':by_product,'data_quality':quality}

def outputs(tables,mode):
    folder = ROOT / 'data/processed'
    folder.mkdir(parents=True, exist_ok=True)
    (ROOT / 'database').mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ROOT/'database/retail_analysis.sqlite') as con:
        for k,df in tables.items():
            df.to_csv(folder/f'{k}.csv',index=False)
            df.to_sql(k,con,if_exists='replace',index=False)
        con.executescript("""
        CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
        CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(order_month);
        CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(stock_code);
        CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
        """)
    invoices=tables['invoices'];sales=tables['sales'];rfm=tables['rfm'];q=tables['data_quality']
    gross=sales.line_revenue.sum();num_orders=invoices.invoice_no.nunique()
    identified=len(rfm)
    repeat=int((rfm.frequency>=2).sum())
    cancellations=tables['cancellations']
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
    (ROOT/'reports/analysis_summary.md').write_text(text,encoding='utf-8')
    return {'gross':float(gross),'orders':num_orders,'aov':float(gross/num_orders),'repeat_rate':float(repeat/identified if identified else 0),'n_customers':identified,'mode':mode}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['demo','real'],default='demo')
    args=parser.parse_args()
    src=ROOT/('data/demo/online_retail_demo.csv' if args.mode=='demo' else 'data/raw/Online Retail.xlsx')
    raw=read_source(src)
    tables=transform(raw)
    results=outputs(tables,args.mode)
    print(f"Mode: {args.mode.upper()} | rows: {len(raw):,} | gross: £{results['gross']:,.2f} | orders: {results['orders']:,} | AOV: £{results['aov']:,.2f}")
    try:
        from charts import make_charts
        make_charts(tables,args.mode)
    except ImportError:
        print('Charts not generated (matplotlib is not installed).')

if __name__ == '__main__':
    main()