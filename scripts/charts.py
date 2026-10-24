"""Static, labelled previews; interactive Power BI report is built in Desktop."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def make_charts(tables,mode):
    title_note='SYNTHETIC DEMO — NOT REAL SALES' if mode=='demo' else 'UCI Online Retail / historical'
    monthly=tables['monthly_sales'].sort_values('order_month')
    fig,ax=plt.subplots(figsize=(10,4.7))
    ax.plot(monthly.order_month,monthly.gross_sales,marker='o')
    ax.set_title(f'Monthly gross merchandise sales (£)\n{title_note}')
    ax.set_ylabel('GBP');ax.set_xlabel('Order month');ax.grid(axis='y',alpha=.3)
    plt.xticks(rotation=45,ha='right');fig.tight_layout();fig.savefig(ROOT/'figures/monthly_sales.png',dpi=160);plt.close(fig)
    seg=tables['rfm'].segment.value_counts().sort_values()
    fig,ax=plt.subplots(figsize=(9,4.5))
    ax.barh(seg.index,seg.values)
    ax.set_title(f'RFM customer segmentation\n{title_note}');ax.set_xlabel('Identified customers')
    fig.tight_layout();fig.savefig(ROOT/'figures/rfm_segments.png',dpi=160);plt.close(fig)
    country=tables['country_sales'].head(8).sort_values('gross_sales')
    fig,ax=plt.subplots(figsize=(9,4.5))
    ax.barh(country.country,country.gross_sales)
    ax.set_title(f'Gross merchandise sales by country\n{title_note}');ax.set_xlabel('GBP')
    fig.tight_layout();fig.savefig(ROOT/'figures/sales_by_country.png',dpi=160);plt.close(fig)
    print('Saved 3 charts to figures/')